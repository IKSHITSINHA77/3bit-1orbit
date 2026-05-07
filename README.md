🚨 ZeroHour
AI-Powered Real-Time Crisis Intelligence Platform
ZeroHour is a real-time crisis intelligence platform that detects and analyzes emergency events from social media signals using AI, NLP, and real-time analytics.

The system ingests social data, classifies severity using LLM + NLP models, verifies information with authoritative sources, clusters signals into incidents, and visualizes everything on a live intelligence dashboard.

🌍 Why ZeroHour

During emergencies, social media signals appear before official reports.

ZeroHour transforms noisy social signals into:

• Early crisis detection
• Real-time monitoring
• Incident intelligence
• Crisis escalation prediction

This system helps analysts, journalists, and emergency response teams detect developing crises faster.

🧠 Key Features
🚨 Real-Time Crisis Detection
Monitors social media signals continuously
Detects emerging incidents
Classifies crisis severity

Severity levels:

CRITICAL
HIGH
MEDIUM
LOW
NEUTRAL
🧠 AI Analysis Pipeline

ZeroHour uses multiple AI models to analyze signals.

Task	Model
Sentiment Analysis	VADER
Crisis Classification	Phi-3
Topic Detection	BERTopic
Entity Recognition	spaCy
Similarity Detection	Sentence Transformers
🔎 Incident Clustering

Instead of analyzing tweets individually, ZeroHour groups related signals into incidents.

Example:

Tweet 1: Explosion heard near station
Tweet 2: Smoke near railway station
Tweet 3: Loud blast downtown

→ Clustered into

Incident #104
Type: Explosion
Location: Downtown Station
Signals: 42
Severity: CRITICAL

Clustering methods:

TF-IDF similarity
Sentence embeddings
Keyword grouping
🗺 Real-Time Crisis Map

ZeroHour visualizes incidents geographically.

Features:

• Incident markers
• Geo-tagged tweets
• Crisis heatmaps
• Regional activity clusters

Built using:

Mapbox
Folium
Streamlit Map components
📈 Event Timeline Analytics

Track how a crisis evolves.

Visualizations:

Tweet Volume vs Time
Sentiment vs Time
Severity Escalation

Detects:

sudden spikes
emotional surges
incident acceleration
🧾 Named Entity Recognition (NER)

Extracts structured entities from tweets.

Example:

Explosion near Delhi railway station

Extracted entities:

Location → Delhi Railway Station
Event → Explosion
Organization → Railway

Used for:

incident clustering
geo-mapping
authority verification
🔍 Authority Verification Engine

ZeroHour checks claims against trusted sources.

Example query:

explosion downtown site:reuters.com OR site:apnews.com

Process:

Search authoritative domains
Scrape results
Verify keyword presence
Mark signal as verified

Output:

authority = TRUE
⚠️ Misinformation Detection

Signals are categorized as:

Verified
Unverified
Likely Misinformation

Factors used:

source credibility
authority confirmation
linguistic patterns
🚨 Crisis Prediction Engine

Predicts whether incidents will escalate.

Model inputs:

tweet velocity
sentiment drop
keyword intensity
source credibility

Example output:

Escalation Probability: 82%
🔔 Automated Alert System

ZeroHour can notify responders automatically.

Trigger example:

severity = CRITICAL
tweet volume > 50
sentiment < -0.7

Alert channels:

• Email
• Slack
• Telegram
• Webhooks

Example alert:

🚨 CRITICAL EVENT DETECTED
Location: Bangalore
Signals: 120
Sentiment: -0.83
📊 Interactive Intelligence Dashboard

The dashboard built with Streamlit shows:

KPI Metrics

• Total Signals
• Active Incidents
• Critical Alerts
• Verified Signals
• Average Sentiment

Visualizations

• Emotion Velocity Chart
• Incident Map
• Severity Distribution
• Crisis Timeline
• Activity Heatmap

Live Signal Feed

Each signal card shows:

severity label
tweet content
username
timestamp
sentiment score
authority status
🌐 Multi-Source Data Ingestion

ZeroHour collects signals from multiple platforms.

Sources:

• Twitter
• Reddit
• Telegram
• RSS News feeds
• Government alerts
• Weather APIs

🧱 System Architecture
Social Media Sources
        │
        ▼
Data Ingestion Layer
(snscrape / APIs)
        │
        ▼
Preprocessing Pipeline
        │
        ▼
AI Analysis Engine
(VADER + LLM + NER)
        │
        ▼
Incident Clustering
        │
        ▼
Authority Verification
        │
        ▼
Database Layer
(SQLite / PostgreSQL)
        │
        ▼
FastAPI Backend
        │
        ▼
Streamlit Intelligence Dashboard


🗄 Database Schema
Tweets Table
Column	Description
tweet_id	unique id
content	tweet text
created_at	timestamp
sentiment	VADER score
severity	classification
authority	verified flag
location	geo tag
Incidents Table
Column	Description
incident_id	id
severity	severity
location	event location
tweet_count	number of signals
escalation_probability	ML prediction
Alerts Table

Stores alert history.

🔌 REST API

Backend powered by FastAPI.

Key endpoints:

GET /api/tweets
POST /api/tweets
GET /api/incidents
POST /api/incidents
GET /api/stats
GET /api/emotion-velocity
POST /api/alerts

Interactive API docs:

http://localhost:8000/docs
⚡ Tech Stack
Layer	Technology
Backend API	FastAPI
Dashboard	Streamlit
AI Models	Phi-3
NLP	spaCy
Sentiment	VADER
Topic Modeling	BERTopic
Database	PostgreSQL
Scraping	snscrape
Data Processing	Pandas
🚀 Future Roadmap

Planned features:

crisis knowledge graph
satellite imagery integration
disaster simulation
edge AI monitoring
global crisis detection network
💡 Use Cases

ZeroHour can be used by:

• disaster response teams
• government agencies
• journalists
• crisis monitoring centers
• intelligence analysts

📜 License

MIT License

🤝 Contributing

Contributions are welcome.

Steps:

1 Fork the repository
2 Create feature branch
3 Commit changes
4 Submit pull request
👨‍💻 Author

ZeroHour — AI Crisis Intelligence System
