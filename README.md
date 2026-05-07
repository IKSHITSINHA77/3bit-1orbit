# 🚨 ZeroHour — AI-Powered Real-Time Crisis Intelligence Platform

ZeroHour is a real-time crisis intelligence platform that detects and analyzes emergency events from social media signals using AI, NLP, and real-time analytics. 

The system ingests social data, classifies severity using LLM + NLP models, verifies information with authoritative sources, clusters signals into incidents, and visualizes everything on a live intelligence dashboard.

<<<<<<< HEAD
```
zerohour/
├── backend/
│   ├── __init__.py
│   ├── database.py      # SQLite setup, queries, helpers
│   ├── sentiment.py     # VADER + Ollama/phi3:mini analysis pipeline
│   ├── authority.py     # Google search + BeautifulSoup authority checker
│   ├── ingest.py        # Mock data injection + snscrape Twitter scraper
│   └── api.py           # FastAPI REST API endpoints
├── frontend/
│   └── dashboard.py     # Streamlit dashboard (main entry point)
├── data/                # Auto-created — holds zerohour.db
├── requirements.txt
└── README.md
```
=======
🌍 **Why ZeroHour?**
During emergencies, social media signals appear before official reports. ZeroHour transforms noisy social signals into:
- **Early crisis detection**
- **Real-Time monitoring**
- **Incident intelligence**
- **Crisis escalation prediction**
>>>>>>> b7bb72278f226c219e4c599dfcd129d31a764c4e

---

## 🧩 Key Features

### 🚨 Real-Time Crisis Detection
- **Continuous Monitoring**: Scans social media signals in real-time.
- **Incident Detection**: Identifies emerging crises before they go viral.
- **Severity Classification**: Labels events as `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `NEUTRAL`.

### 🔥 Incident Clustering (NEW)
Groups individual signals into cohesive incidents to reduce noise.
- **Example**: 20 tweets about a "smoke near station" → **Incident #104: Fire at Central Station**.
- **Methods**: TF-IDF similarity, Sentence Embeddings (MiniLM), and Keyword Grouping.

### 📍 Live Crisis Map (NEW)
Visualizes incidents geographically for better situational awareness.
- **Incident Markers**: Clickable markers showing event details.
- **Heatmaps**: Regional activity clusters indicating crisis intensity.
- **Tools**: Built with Mapbox, Folium, and Streamlit components.

### 🧠 Advanced AI Analysis Pipeline
ZeroHour uses a multi-model approach for deep intelligence:
| Task | Model |
| --- | --- |
| **Sentiment Analysis** | VADER (Rule-based, instant) |
| **Crisis Classification** | Phi-3 (Context-aware LLM) |
| **Topic Detection** | BERTopic |
| **Entity Extraction (NER)** | spaCy |

### 🔍 Authority Verification & Misinformation Detection
- **Authority Engine**: Checks claims against trusted sources (Reuters, AP, Police.gov).
- **Misinformation Detection**: Categorizes signals as *Verified*, *Unverified*, or *Likely Misinformation* based on source credibility and linguistic patterns.

### 🚨 Crisis Prediction & Early Warning
- **Escalation Model**: Predicts the probability of an incident escalating based on tweet velocity, sentiment drop, and keyword intensity.
- **Emotion Surge Detection**: Automatically alerts responders when sudden negative emotional spikes are detected.

### 4. (Optional) Start the REST API server

```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**

---

## 🔌 REST API (Powered by FastAPI)

<<<<<<< HEAD
| Category | Tool | Why |
|---|---|---|
| 🚀 LLM Runtime | **Ollama** | Single install, excellent DX, no compilation |
| 🤖 LLM Model | **Phi-3-mini (3.8B, 4-bit)** | ~2.5 GB RAM, GPT-3.5 competitive quality |
| 📈 Dashboard | **Streamlit** | Fastest Python dashboard framework |
| � REST API | **FastAPI** | High-performance async API with automatic docs |
| � Database | **SQLite** | Zero config, built-in Python, WAL concurrency |
| 📊 Data Processing | **Pandas** | Aggregation & window functions on tweet windows |
| 😡 Sentiment | **VADER** | Rule-based, instant, great for social media slang |
| 🔍 Web Scraping | **BeautifulSoup + googlesearch-python** | Authority verification without API keys |
| 📡 Data Ingestion | **snscrape** | Twitter scraping without API keys |
| 🐍 Language | **Python 3.9+** | Universal compatibility across the whole stack |
=======
ZeroHour includes a robust backend for programmatic access.
- **Interactive Docs**: Available at `http://localhost:8000/docs`
- **Key Endpoints**:
  - `GET /api/tweets` - Retrieve all ingested signals.
  - `GET /api/incidents` - Get clustered incidents.
  - `GET /api/stats` - Fetch real-time dashboard KPIs.
  - `POST /api/alerts` - Configure and trigger custom alerts.
>>>>>>> b7bb72278f226c219e4c599dfcd129d31a764c4e

---

## 📈 Dashboard Features (Streamlit)

- **KPI Metrics**: Total Signals, Active Incidents, Critical Alerts, Verified Signals.
- **Emotion Velocity Chart**: Real-time visualization of sentiment trends.
- **Incident Explorer**: Drill down into specific events to see timelines, news links, and maps.
- **Smart Search**: Filter by location, keyword, time, or severity.

---

<<<<<<< HEAD
## 🔌 REST API

ZeroHour includes a FastAPI REST API for programmatic access to all database operations.

### Start the API Server

```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**

### API Endpoints

#### Tweets
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/tweets` | Create a new tweet |
| GET | `/api/tweets` | Get all tweets (with optional severity filter) |
| GET | `/api/tweets/{tweet_id}` | Get a specific tweet by ID |
| PUT | `/api/tweets/{tweet_id}` | Update a tweet by ID |
| DELETE | `/api/tweets/{tweet_id}` | Delete a tweet by ID |
| POST | `/api/tweets/batch` | Create multiple tweets in batch |

#### Incidents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/incidents` | Create a new incident |
| GET | `/api/incidents` | Get all incidents (with optional severity filter) |
| GET | `/api/incidents/{incident_id}` | Get a specific incident by ID |
| PUT | `/api/incidents/{incident_id}` | Update an incident by ID |
| DELETE | `/api/incidents/{incident_id}` | Delete an incident by ID |

#### Analysis Log
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analysis-log` | Get analysis log entries |
| POST | `/api/analysis-log` | Create a new analysis log entry |

#### Statistics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/stats` | Get dashboard statistics |
| GET | `/api/emotion-velocity` | Get emotion velocity data |

#### Database Management
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/database/info` | Get database information |
| POST | `/api/database/reset` | Reset the database (WARNING: deletes all data) |

### Example API Usage

**Create a tweet:**
```bash
curl -X POST "http://localhost:8000/api/tweets" \
  -H "Content-Type: application/json" \
  -d '{
    "tweet_id": "123456789",
    "username": "@user",
    "content": "Emergency situation reported downtown",
    "created_at": "2024-01-01T12:00:00",
    "source": "api",
    "location": "New York",
    "llm_label": "HIGH",
    "llm_score": 0.85
  }'
```

**Get all tweets:**
```bash
curl "http://localhost:8000/api/tweets?limit=50&severity=CRITICAL"
```

**Get statistics:**
```bash
curl "http://localhost:8000/api/stats"
```

---

## 🔬 Analysis Pipeline
=======
## 🚀 Roadmap: Best 8 Features (Priority)
>>>>>>> b7bb72278f226c219e4c599dfcd129d31a764c4e

These are currently being implemented to make ZeroHour a world-class platform:
1.  **Live Crisis Map**: Interactive geospatial visualization of events.
2.  **Incident Clustering**: Automatic grouping of related signals.
3.  **Alert System**: Real-time notifications via Email/Telegram/Slack.
4.  **NER Location Extraction**: Pinpointing exact locations from tweet text.
5.  **Topic Classification**: Identifying specific disaster types (Flood, Explosion, etc.).
6.  **Event Timeline**: Tracking the evolution of a crisis over time.
7.  **Misinformation Detection**: Ranking signals by credibility.
8.  **Multi-Source Ingestion**: Adding Reddit, Telegram, and RSS feeds.

---

## 🗄️ Tech Stack

| Layer | Technology |
| --- | --- |
| **Backend API** | FastAPI |
| **Dashboard** | Streamlit |
| **AI Models** | Phi-3-mini (LLM), VADER (Sentiment) |
| **NLP** | spaCy, BERTopic |
| **Database** | SQLite (PostgreSQL for production) |
| **Scraping** | snscrape, BeautifulSoup |
| **Geo** | Mapbox, Folium |

---

## 📦 Installation & Setup

1. **Clone & Install**:
   ```bash
   git clone https://github.com/yourname/zerohour.git
   cd zerohour
   pip install -r requirements.txt
   ```
2. **Setup Ollama** (Optional but recommended):
   - Install from [ollama.com](https://ollama.com)
   - Run `ollama pull phi3:mini`
3. **Launch**:
   ```bash
   # Start API
   uvicorn backend.main:app --reload
   
   # Start Dashboard
   streamlit run frontend/dashboard.py
   ```

---

<<<<<<< HEAD
## 🚀 Tips

- **No Ollama?** The dashboard fully works with VADER-only mode. All labels still appear.
- **Demo mode**: Click "Inject Mock Data" for instant realistic data across all severity levels.
- **REST API**: Use the FastAPI backend for programmatic access to all database operations. See the API section above.
- **Extend it**: The API already includes webhook-ready endpoints. Add authentication with `fastapi.security`.
- **Scale it**: Swap SQLite for PostgreSQL by changing the connection string in `database.py`.
- **Auth layer**: Add `st.secrets` for API keys and wrap the dashboard with `streamlit-authenticator`.

---
=======
## 📜 License
MIT License. Created by ZeroHour Team.
>>>>>>> b7bb72278f226c219e4c599dfcd129d31a764c4e
