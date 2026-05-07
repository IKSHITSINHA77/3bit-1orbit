"""
ZeroHour — Real-Time Crisis Intelligence Dashboard
Run with:  streamlit run frontend/dashboard.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import pandas as pd
import streamlit as st
from datetime import datetime

from backend.database import init_db, fetch_tweets, fetch_stats, fetch_emotion_velocity
from backend.ingest import seed_mock_data, scrape_twitter
from backend.sentiment import analyze

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZeroHour | Crisis Monitor",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

      html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
      h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

      /* Dark cockpit feel */
      .stApp { background: #0b0d12; color: #e2e8f0; }
      section[data-testid="stSidebar"] { background: #111420 !important; }

      /* Severity badges */
      .badge-CRITICAL { background:#ff2d55; color:#fff; padding:3px 10px; border-radius:4px; font-weight:700; font-size:0.78rem; }
      .badge-HIGH     { background:#ff9f0a; color:#000; padding:3px 10px; border-radius:4px; font-weight:700; font-size:0.78rem; }
      .badge-MEDIUM   { background:#ffd60a; color:#000; padding:3px 10px; border-radius:4px; font-weight:700; font-size:0.78rem; }
      .badge-LOW      { background:#30d158; color:#000; padding:3px 10px; border-radius:4px; font-weight:700; font-size:0.78rem; }
      .badge-NEUTRAL  { background:#3a3f55; color:#aaa; padding:3px 10px; border-radius:4px; font-size:0.78rem; }

      /* Metric card overrides */
      [data-testid="stMetric"] { background:#161926; border:1px solid #252a3d; border-radius:10px; padding:16px 20px; }
      [data-testid="stMetricValue"] { font-family:'Space Mono',monospace; font-size:2rem !important; }

      /* Scrollable tweet feed */
      .tweet-card {
        background: #161926;
        border-left: 4px solid #3a3f55;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: border-color 0.2s;
      }
      .tweet-card.CRITICAL { border-left-color: #ff2d55; }
      .tweet-card.HIGH     { border-left-color: #ff9f0a; }
      .tweet-card.MEDIUM   { border-left-color: #ffd60a; }
      .tweet-card.LOW      { border-left-color: #30d158; }

      .tweet-meta { font-size:0.75rem; color:#6b7280; margin-top:6px; }
      .tweet-content { font-size:0.92rem; line-height:1.55; color:#cbd5e1; margin:6px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚨 ZeroHour")
    st.caption("Real-Time Crisis Intelligence")
    st.divider()

    st.markdown("### ⚙️ Controls")
    if st.button("💉 Inject Mock Data", use_container_width=True, type="primary"):
        n = seed_mock_data()
        st.success(f"Injected {n} mock tweets!")
        time.sleep(0.5)
        st.rerun()

    st.divider()
    st.markdown("### 🔍 Live Scraper")
    query = st.text_input("Search query", placeholder="fire flood earthquake...")
    scrape_limit = st.slider("Max tweets", 5, 100, 20)
    if st.button("🐦 Scrape Twitter", use_container_width=True):
        with st.spinner("Scraping..."):
            n = scrape_twitter(query, scrape_limit)
        st.info(f"Inserted {n} tweets from scrape.")
        st.rerun()

    st.divider()
    st.markdown("### 🧪 Analyze Tweet")
    test_tweet = st.text_area("Paste a tweet to analyze", height=80)
    if st.button("Analyze", use_container_width=True) and test_tweet:
        with st.spinner("Analyzing..."):
            result = analyze(test_tweet)
        label = result["llm_label"]
        st.markdown(f"**Label:** <span class='badge-{label}'>{label}</span>", unsafe_allow_html=True)
        st.metric("VADER", result["raw_vader"])
        st.metric("LLM Score", result["llm_score"])
        st.caption(result.get("reasoning", ""))

    st.divider()
    st.markdown("### 🔎 Filters")
    severity_filter = st.multiselect(
        "Severity",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEUTRAL"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEUTRAL"],
    )
    show_limit = st.slider("Max records", 20, 300, 100)
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(30)
    st.rerun()

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='margin-bottom:0'>🚨 ZeroHour</h1>"
    "<p style='color:#6b7280;font-size:0.9rem;margin-top:4px'>"
    f"Crisis Intelligence Dashboard &nbsp;·&nbsp; Last refresh: {datetime.now().strftime('%H:%M:%S')}"
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Fetch data ────────────────────────────────────────────────────────────────
stats = fetch_stats()
all_tweets = fetch_tweets(limit=show_limit)
df = pd.DataFrame(all_tweets)

if not df.empty and severity_filter:
    df = df[df["llm_label"].isin(severity_filter)]

# ── KPI Row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📡 Total Signals", stats["total"])
c2.metric("🔴 CRITICAL", stats["critical"])
c3.metric("🟠 HIGH", stats["high"])
c4.metric("✅ Authority Confirmed", stats["authority_confirmed"])
c5.metric("😡 Avg Sentiment", stats["avg_sentiment"])

st.divider()

# ── Charts Row ────────────────────────────────────────────────────────────────
col_chart1, col_chart2 = st.columns([1.6, 1])

with col_chart1:
    st.markdown("#### 📈 Emotion Velocity (last 60 min)")
    vel = fetch_emotion_velocity(60)
    if vel:
        vel_df = pd.DataFrame(vel).rename(columns={"minute": "Time", "avg_vader": "Avg VADER", "count": "Volume"})
        vel_df = vel_df.set_index("Time")
        st.line_chart(vel_df[["Avg VADER"]], height=220, use_container_width=True)
    else:
        st.info("No time-series data yet — inject mock data to populate.")

with col_chart2:
    st.markdown("#### 🎯 Severity Distribution")
    if not df.empty:
        dist = df["llm_label"].value_counts().reset_index()
        dist.columns = ["Severity", "Count"]
        st.bar_chart(dist.set_index("Severity"), height=220, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# ── Tweet Feed ────────────────────────────────────────────────────────────────
st.markdown("#### 📋 Live Feed")

if df.empty:
    st.warning("No tweets found. Click **Inject Mock Data** in the sidebar to get started.")
else:
    for _, row in df.iterrows():
        label = row.get("llm_label", "NEUTRAL")
        score = row.get("llm_score", 0)
        vader = row.get("raw_vader", 0)
        authority = "✅ Authority" if row.get("authority") else ""
        location = f"📍 {row['location']}" if row.get("location") else ""
        ts = row.get("created_at", "")[:16].replace("T", " ")

        st.markdown(
            f"""
            <div class="tweet-card {label}">
              <span class="badge-{label}">{label}</span>&nbsp;{authority}
              <div class="tweet-content">{row['content']}</div>
              <div class="tweet-meta">
                <strong>{row.get('username','@unknown')}</strong>
                &nbsp;·&nbsp; {ts}
                &nbsp;·&nbsp; {location}
                &nbsp;·&nbsp; VADER: {vader:.2f}
                &nbsp;·&nbsp; Score: {score:.2f}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("ZeroHour · Built for hackathon · Phi-3-mini + VADER + SQLite + Streamlit")
