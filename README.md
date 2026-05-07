# 🚨 ZeroHour — AI-Powered Real-Time Crisis Intelligence Platform

ZeroHour is a real-time crisis intelligence platform that detects and analyzes emergency events from social media signals using AI, NLP, and real-time analytics. 

The system ingests social data, classifies severity using LLM + NLP models, verifies information with authoritative sources, clusters signals into incidents, and visualizes everything on a live intelligence dashboard.

🌍 **Why ZeroHour?**
During emergencies, social media signals appear before official reports. ZeroHour transforms noisy social signals into:
- **Early crisis detection**
- **Real-Time monitoring**
- **Incident intelligence**
- **Crisis escalation prediction**

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

---

## 🔌 REST API (Powered by FastAPI)

ZeroHour includes a robust backend for programmatic access.
- **Interactive Docs**: Available at `http://localhost:8000/docs`
- **Key Endpoints**:
  - `GET /api/tweets` - Retrieve all ingested signals.
  - `GET /api/incidents` - Get clustered incidents.
  - `GET /api/stats` - Fetch real-time dashboard KPIs.
  - `POST /api/alerts` - Configure and trigger custom alerts.

---

## 📈 Dashboard Features (Streamlit)

- **KPI Metrics**: Total Signals, Active Incidents, Critical Alerts, Verified Signals.
- **Emotion Velocity Chart**: Real-time visualization of sentiment trends.
- **Incident Explorer**: Drill down into specific events to see timelines, news links, and maps.
- **Smart Search**: Filter by location, keyword, time, or severity.

---

## 🚀 Roadmap: Best 8 Features (Priority)

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

## 📜 License
MIT License. Created by ZeroHour Team.
