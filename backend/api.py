"""
ZeroHour - FastAPI REST API for database operations.

Provides RESTful endpoints for:
- Tweets CRUD operations
- Incidents CRUD operations
- Analysis log access
- Statistics and analytics
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import sqlite3
import os
import io

from backend.database import (
    get_connection,
    init_db,
    insert_tweet,
    fetch_tweets,
    fetch_stats,
    fetch_emotion_velocity,
)
from backend.image_processor import process_uploaded_image

# Initialize FastAPI app
app = FastAPI(
    title="ZeroHour API",
    description="REST API for ZeroHour Crisis Intelligence Dashboard",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# ── Pydantic Models for Request/Response ──────────────────────────────────────

class TweetCreate(BaseModel):
    tweet_id: str
    username: str
    content: str
    created_at: str
    source: str = "api"
    location: Optional[str] = None
    keywords: Optional[str] = None
    raw_vader: Optional[float] = None
    llm_label: Optional[str] = None
    llm_score: Optional[float] = None
    authority: int = 0


class TweetUpdate(BaseModel):
    username: Optional[str] = None
    content: Optional[str] = None
    location: Optional[str] = None
    keywords: Optional[str] = None
    raw_vader: Optional[float] = None
    llm_label: Optional[str] = None
    llm_score: Optional[float] = None
    authority: Optional[int] = None


class TweetResponse(BaseModel):
    id: int
    tweet_id: str
    username: str
    content: str
    created_at: str
    source: str
    location: Optional[str]
    keywords: Optional[str]
    raw_vader: Optional[float]
    llm_label: Optional[str]
    llm_score: Optional[float]
    authority: int
    ingested_at: str


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    location: Optional[str] = None
    tweet_ids: Optional[str] = None
    authority_confirmed: int = 0


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    location: Optional[str] = None
    tweet_ids: Optional[str] = None
    authority_confirmed: Optional[int] = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    severity: str
    location: Optional[str]
    tweet_ids: Optional[str]
    authority_confirmed: int
    created_at: str
    updated_at: str


class AnalysisLogResponse(BaseModel):
    id: int
    tweet_id: int
    stage: str
    result: str
    latency_ms: Optional[float]
    created_at: str


class StatsResponse(BaseModel):
    total: int
    critical: int
    high: int
    authority_confirmed: int
    avg_sentiment: float


class EmotionVelocityResponse(BaseModel):
    minute: str
    avg_vader: float
    count: int


class ImageAnalysisResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    error: Optional[str] = None
    text: Optional[str] = None
    confidence: Optional[float] = None
    word_count: Optional[int] = None
    processing_time: Optional[float] = None
    crisis_detected: Optional[bool] = None
    severity: Optional[str] = None
    sentiment_analysis: Optional[dict] = None


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ZeroHour API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "tweets": "/api/tweets",
            "incidents": "/api/incidents",
            "analysis_log": "/api/analysis-log",
            "stats": "/api/stats",
            "emotion_velocity": "/api/emotion-velocity",
            "image_analysis": "/api/image/analyze",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ── Tweets Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/tweets", response_model=TweetResponse, status_code=201)
async def create_tweet(tweet: TweetCreate):
    """Create a new tweet entry."""
    try:
        tweet_data = tweet.dict()
        row_id = insert_tweet(tweet_data)
        if row_id:
            # Fetch the created tweet
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM tweets WHERE id = ?", (row_id,)
                ).fetchone()
                if row:
                    return dict(row)
        raise HTTPException(status_code=400, detail="Failed to create tweet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tweets", response_model=List[TweetResponse])
async def get_tweets(
    limit: int = Query(200, ge=1, le=1000),
    severity: Optional[str] = Query(None, pattern="^(CRITICAL|HIGH|MEDIUM|LOW|NEUTRAL)$")
):
    """Get tweets with optional filtering by severity."""
    try:
        tweets = fetch_tweets(limit=limit, severity=severity)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tweets/{tweet_id}", response_model=TweetResponse)
async def get_tweet(tweet_id: str):
    """Get a specific tweet by ID."""
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tweets WHERE tweet_id = ?", (tweet_id,)
            ).fetchone()
            if row:
                return dict(row)
        raise HTTPException(status_code=404, detail="Tweet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tweets/{tweet_id}", response_model=TweetResponse)
async def update_tweet(tweet_id: str, tweet: TweetUpdate):
    """Update a tweet by ID."""
    try:
        with get_connection() as conn:
            # Check if tweet exists
            existing = conn.execute(
                "SELECT * FROM tweets WHERE tweet_id = ?", (tweet_id,)
            ).fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Tweet not found")
            
            # Build update query dynamically
            update_data = {k: v for k, v in tweet.dict().items() if v is not None}
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [tweet_id]
            
            conn.execute(
                f"UPDATE tweets SET {set_clause} WHERE tweet_id = ?",
                values
            )
            conn.commit()
            
            # Fetch updated tweet
            row = conn.execute(
                "SELECT * FROM tweets WHERE tweet_id = ?", (tweet_id,)
            ).fetchone()
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tweets/{tweet_id}")
async def delete_tweet(tweet_id: str):
    """Delete a tweet by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM tweets WHERE tweet_id = ?", (tweet_id,)
            )
            conn.commit()
            if cursor.rowcount > 0:
                return {"message": "Tweet deleted successfully"}
            raise HTTPException(status_code=404, detail="Tweet not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Incidents Endpoints ───────────────────────────────────────────────────────

@app.post("/api/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(incident: IncidentCreate):
    """Create a new incident."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO incidents (title, description, severity, location, tweet_ids, authority_confirmed)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (incident.title, incident.description, incident.severity, 
                 incident.location, incident.tweet_ids, incident.authority_confirmed)
            )
            conn.commit()
            
            # Fetch created incident
            row = conn.execute(
                "SELECT * FROM incidents WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/incidents", response_model=List[IncidentResponse])
async def get_incidents(
    limit: int = Query(100, ge=1, le=500),
    severity: Optional[str] = Query(None, pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$")
):
    """Get incidents with optional filtering by severity."""
    try:
        with get_connection() as conn:
            if severity:
                rows = conn.execute(
                    "SELECT * FROM incidents WHERE severity = ? ORDER BY created_at DESC LIMIT ?",
                    (severity, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int):
    """Get a specific incident by ID."""
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if row:
                return dict(row)
        raise HTTPException(status_code=404, detail="Incident not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: int, incident: IncidentUpdate):
    """Update an incident by ID."""
    try:
        with get_connection() as conn:
            # Check if incident exists
            existing = conn.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Incident not found")
            
            # Build update query dynamically
            update_data = {k: v for k, v in incident.dict().items() if v is not None}
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [incident_id]
            
            conn.execute(
                f"UPDATE incidents SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
                values
            )
            conn.commit()
            
            # Fetch updated incident
            row = conn.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/incidents/{incident_id}")
async def delete_incident(incident_id: int):
    """Delete an incident by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM incidents WHERE id = ?", (incident_id,)
            )
            conn.commit()
            if cursor.rowcount > 0:
                return {"message": "Incident deleted successfully"}
            raise HTTPException(status_code=404, detail="Incident not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analysis Log Endpoints ────────────────────────────────────────────────────

@app.get("/api/analysis-log", response_model=List[AnalysisLogResponse])
async def get_analysis_log(
    limit: int = Query(100, ge=1, le=1000),
    tweet_id: Optional[int] = None
):
    """Get analysis log entries with optional filtering by tweet ID."""
    try:
        with get_connection() as conn:
            if tweet_id:
                rows = conn.execute(
                    "SELECT * FROM analysis_log WHERE tweet_id = ? ORDER BY created_at DESC LIMIT ?",
                    (tweet_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM analysis_log ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analysis-log", response_model=AnalysisLogResponse, status_code=201)
async def create_analysis_log(
    tweet_id: int,
    stage: str,
    result: str,
    latency_ms: Optional[float] = None
):
    """Create a new analysis log entry."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_log (tweet_id, stage, result, latency_ms)
                VALUES (?, ?, ?, ?)
                """,
                (tweet_id, stage, result, latency_ms)
            )
            conn.commit()
            
            # Fetch created log entry
            row = conn.execute(
                "SELECT * FROM analysis_log WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Statistics Endpoints ───────────────────────────────────────────────────────

@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics():
    """Get dashboard statistics."""
    try:
        stats = fetch_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emotion-velocity", response_model=List[EmotionVelocityResponse])
async def get_emotion_velocity(
    window_minutes: int = Query(60, ge=1, le=1440)
):
    """Get emotion velocity data for the specified time window."""
    try:
        velocity = fetch_emotion_velocity(window_minutes=window_minutes)
        return velocity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Batch Operations ───────────────────────────────────────────────────────────

@app.post("/api/tweets/batch", response_model=List[TweetResponse])
async def create_tweets_batch(tweets: List[TweetCreate]):
    """Create multiple tweets in a batch."""
    try:
        created_tweets = []
        for tweet in tweets:
            tweet_data = tweet.dict()
            row_id = insert_tweet(tweet_data)
            if row_id:
                with get_connection() as conn:
                    row = conn.execute(
                        "SELECT * FROM tweets WHERE id = ?", (row_id,)
                    ).fetchone()
                    if row:
                        created_tweets.append(dict(row))
        return created_tweets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Database Management ───────────────────────────────────────────────────────

@app.post("/api/database/reset")
async def reset_database():
    """Reset the database (WARNING: This will delete all data)."""
    try:
        DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "zerohour.db")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        return {"message": "Database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/database/info")
async def get_database_info():
    """Get database information."""
    try:
        DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "zerohour.db")
        with get_connection() as conn:
            # Get table counts
            tweets_count = conn.execute("SELECT COUNT(*) FROM tweets").fetchone()[0]
            incidents_count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
            log_count = conn.execute("SELECT COUNT(*) FROM analysis_log").fetchone()[0]
            
            # Get database size
            db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
            
            return {
                "database_path": DB_PATH,
                "database_size_bytes": db_size,
                "tables": {
                    "tweets": tweets_count,
                    "incidents": incidents_count,
                    "analysis_log": log_count
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Image Processing Endpoints ─────────────────────────────────────────────────────

@app.post("/api/image/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Upload and analyze an image for text extraction and crisis detection.
    
    Args:
        file: Image file to analyze
        
    Returns:
        Analysis results including extracted text and crisis intelligence
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        image_data = await file.read()
        
        # Process image
        result = process_uploaded_image(image_data, file.filename)
        
        if not result['success']:
            return ImageAnalysisResponse(
                success=False,
                filename=file.filename,
                error=result.get('error', 'Unknown error')
            )
        
        analysis = result['analysis']
        
        # If crisis detected, create a tweet entry
        if analysis.get('crisis_detected') and analysis.get('text'):
            tweet_data = {
                "tweet_id": f"img_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "username": "@image_analysis",
                "content": f"[IMAGE] {analysis['text'][:200]}...",
                "created_at": datetime.utcnow().isoformat(),
                "source": "image_ocr",
                "location": None,
                "keywords": "image_analysis,ocr",
                "raw_vader": analysis.get('sentiment_analysis', {}).get('raw_vader', 0),
                "llm_label": analysis.get('severity', 'NEUTRAL'),
                "llm_score": analysis.get('sentiment_analysis', {}).get('llm_score', 0),
                "authority": 0,
            }
            insert_tweet(tweet_data)
        
        return ImageAnalysisResponse(
            success=True,
            filename=result['filename'],
            text=analysis.get('text'),
            confidence=analysis.get('confidence'),
            word_count=analysis.get('word_count'),
            processing_time=analysis.get('processing_time'),
            crisis_detected=analysis.get('crisis_detected'),
            severity=analysis.get('severity'),
            sentiment_analysis=analysis.get('sentiment_analysis')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/image/supported-formats")
async def get_supported_formats():
    """Get list of supported image formats."""
    return {
        "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
        "max_size_mb": 10,
        "min_dimensions": {"width": 50, "height": 50},
        "max_dimensions": {"width": 5000, "height": 5000}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
