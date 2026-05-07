"""
ZeroHour - SQLite database setup and helpers.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "zerohour.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # concurrent reads
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tweets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id    TEXT UNIQUE,
                username    TEXT,
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                source      TEXT DEFAULT 'mock',
                location    TEXT,
                keywords    TEXT,
                raw_vader   REAL,
                llm_label   TEXT,
                llm_score   REAL,
                authority   INTEGER DEFAULT 0,
                ingested_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                description  TEXT,
                severity     TEXT CHECK(severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
                location     TEXT,
                tweet_ids    TEXT,
                authority_confirmed INTEGER DEFAULT 0,
                created_at   TEXT DEFAULT (datetime('now')),
                updated_at   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS analysis_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id    INTEGER REFERENCES tweets(id),
                stage       TEXT,
                result      TEXT,
                latency_ms  REAL,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            """
        )
    print(f"[DB] Initialized → {DB_PATH}")


def insert_tweet(data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO tweets
                (tweet_id, username, content, created_at, source, location, keywords,
                 raw_vader, llm_label, llm_score, authority)
            VALUES
                (:tweet_id, :username, :content, :created_at, :source, :location,
                 :keywords, :raw_vader, :llm_label, :llm_score, :authority)
            """,
            data,
        )
        return cur.lastrowid


def fetch_tweets(limit: int = 200, severity: str = None) -> list[dict]:
    with get_connection() as conn:
        if severity:
            rows = conn.execute(
                "SELECT * FROM tweets WHERE llm_label = ? ORDER BY created_at DESC LIMIT ?",
                (severity, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tweets ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def fetch_stats() -> dict:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tweets").fetchone()[0]
        critical = conn.execute(
            "SELECT COUNT(*) FROM tweets WHERE llm_label='CRITICAL'"
        ).fetchone()[0]
        high = conn.execute(
            "SELECT COUNT(*) FROM tweets WHERE llm_label='HIGH'"
        ).fetchone()[0]
        authority = conn.execute(
            "SELECT COUNT(*) FROM tweets WHERE authority=1"
        ).fetchone()[0]
        avg_vader = conn.execute(
            "SELECT AVG(raw_vader) FROM tweets"
        ).fetchone()[0] or 0.0
        return {
            "total": total,
            "critical": critical,
            "high": high,
            "authority_confirmed": authority,
            "avg_sentiment": round(avg_vader, 3),
        }


def fetch_emotion_velocity(window_minutes: int = 60) -> list[dict]:
    """Return average VADER per minute bucket for the last N minutes."""
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT
                strftime('%Y-%m-%dT%H:%M', created_at) AS minute,
                AVG(raw_vader) AS avg_vader,
                COUNT(*) AS count
            FROM tweets
            WHERE created_at >= datetime('now', '-{window_minutes} minutes')
            GROUP BY minute
            ORDER BY minute ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
