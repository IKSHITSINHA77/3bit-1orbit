# 3bit-1orbit
# 🚨 ZeroHour — Real-Time Crisis Intelligence Dashboard

ZeroHour ingests social media signals, classifies them by severity using a local LLM (Phi-3-mini via Ollama) with VADER as an instant fallback, verifies claims against authoritative sources, and surfaces everything in a live Streamlit dashboard.

---
## 📁 Project Structure

```
zerohour/
├── backend/
│   ├── __init__.py
│   ├── database.py      # SQLite setup, queries, helpers
│   ├── sentiment.py     # VADER + Ollama/phi3:mini analysis pipeline
│   ├── authority.py     # Google search + BeautifulSoup authority checker
│   └── ingest.py        # Mock data injection + snscrape Twitter scraper
├── frontend/
│   └── dashboard.py     # Streamlit dashboard (main entry point)
├── data/                # Auto-created — holds zerohour.db
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/yourname/zerohour.git
cd zerohour
pip install -r requirements.txt
```

### 2. (Optional) Set up Ollama for LLM analysis

```bash
# Install Ollama: https://ollama.com
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model (~2.5 GB)
ollama pull phi3:mini

# Start the server
ollama serve
```

> **Without Ollama**, ZeroHour automatically falls back to VADER sentiment analysis — the dashboard still works perfectly.

### 3. Launch the dashboard

```bash
streamlit run frontend/dashboard.py
```

Open **http://localhost:8501** in your browser.

---

## 🧩 Tech Stack

| Category | Tool | Why |
|---|---|---|
| 🚀 LLM Runtime | **Ollama** | Single install, excellent DX, no compilation |
| 🤖 LLM Model | **Phi-3-mini (3.8B, 4-bit)** | ~2.5 GB RAM, GPT-3.5 competitive quality |
| 📈 Dashboard | **Streamlit** | Fastest Python dashboard framework |
| 💾 Database | **SQLite** | Zero config, built-in Python, WAL concurrency |
| 📊 Data Processing | **Pandas** | Aggregation & window functions on tweet windows |
| 😡 Sentiment | **VADER** | Rule-based, instant, great for social media slang |
| 🔍 Web Scraping | **BeautifulSoup + googlesearch-python** | Authority verification without API keys |
| 📡 Data Ingestion | **snscrape** | Twitter scraping without API keys |
| 🐍 Language | **Python 3.9+** | Universal compatibility across the whole stack |

---

## 🎮 Dashboard Features

### 📊 KPI Row
- **Total Signals** — all tweets ingested
- **CRITICAL** — highest severity count
- **HIGH** — elevated severity count
- **Authority Confirmed** — tweets verified against official sources
- **Avg Sentiment** — average VADER compound score

### 📈 Emotion Velocity Chart
Line chart of VADER compound scores bucketed by minute over the last 60 minutes. A rapid drop toward -1 indicates an emerging crisis.

### 🎯 Severity Distribution
Bar chart showing the breakdown of tweets across `CRITICAL / HIGH / MEDIUM / LOW / NEUTRAL`.

### 📋 Live Tweet Feed
Color-coded card feed ordered by recency. Each card shows:
- Severity badge and authority confirmation flag
- Tweet content
- Username, timestamp, location, VADER score, LLM confidence score

### 🔧 Sidebar Controls
| Control | Description |
|---|---|
| 💉 Inject Mock Data | Seeds 14 realistic crisis tweets across all severity levels |
| 🐦 Scrape Twitter | Live scrape using snscrape (no API key required) |
| 🧪 Analyze Tweet | Paste any text and see instant VADER + LLM analysis |
| Severity Filter | Multi-select to show only relevant severity levels |
| Auto-refresh | Polls every 30 seconds for a live dashboard feel |

---

## 🔬 Analysis Pipeline

```
Tweet text
    │
    ├─── VADER (instant, always runs)
    │       └── compound score [-1 to +1]
    │
    ├─── Keyword Matcher (regex, instant fallback)
    │       └── CRITICAL / HIGH / MEDIUM based on crisis vocab
    │
    └─── Ollama / phi3:mini (async, 3-10s)
            └── JSON: { label, score, reasoning }
                  │
                  └── Falls back to VADER if Ollama is offline
```

**Severity Labels:** `CRITICAL → HIGH → MEDIUM → LOW → NEUTRAL`

---

## 🔍 Authority Verification

The `authority.py` module:
1. Builds a targeted Google query: `<keywords> site:police.gov OR site:reuters.com OR site:apnews.com`
2. Checks if any result URL is from a known authoritative domain.
3. Fetches the page with BeautifulSoup and confirms keyword presence.
4. Marks the tweet with `authority=1` in the database.

> Runs asynchronously — won't block the ingestion pipeline.

---

## 🗄️ Database Schema

### `tweets`
| Column | Type | Description |
|---|---|---|
| `tweet_id` | TEXT UNIQUE | Original tweet ID or UUID for mocks |
| `content` | TEXT | Raw tweet text |
| `created_at` | TEXT | ISO 8601 timestamp |
| `raw_vader` | REAL | VADER compound score |
| `llm_label` | TEXT | Severity: CRITICAL/HIGH/MEDIUM/LOW/NEUTRAL |
| `llm_score` | REAL | LLM confidence 0–1 |
| `authority` | INTEGER | 1 if authority-confirmed |
| `location` | TEXT | Geo-tag if available |

### `incidents`
Aggregated incident records linked to tweet IDs.

### `analysis_log`
Audit trail of every analysis stage with latency tracking.

---

## 🚀 Tips

- **No Ollama?** The dashboard fully works with VADER-only mode. All labels still appear.
- **Demo mode**: Click "Inject Mock Data" for instant realistic data across all severity levels.
- **Extend it**: Add a `POST /ingest` FastAPI endpoint to accept webhooks from external sources.
- **Scale it**: Swap SQLite for PostgreSQL by changing the connection string in `database.py`.
- **Auth layer**: Add `st.secrets` for API keys and wrap the dashboard with `streamlit-authenticator`.

---



