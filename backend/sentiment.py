"""
ZeroHour - Sentiment analysis layer.

Priority order:
  1. LLM (Ollama / phi3:mini) for rich, context-aware labels.
  2. VADER as an instant fallback when Ollama is unavailable.
"""

import time
import json
import re
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore

_vader = SentimentIntensityAnalyzer()

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"

SEVERITY_LABELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEUTRAL"]

# Keywords that bump severity
CRISIS_KEYWORDS = {
    "CRITICAL": ["explosion", "bombing", "mass shooting", "terror", "attack", "casualty", "fatality", "dead"],
    "HIGH": ["fire", "flood", "earthquake", "riot", "violence", "injured", "missing", "evacuation", "police"],
    "MEDIUM": ["accident", "protest", "arrested", "investigation", "suspicious"],
}


def vader_score(text: str) -> float:
    """Return compound VADER score in [-1, 1]."""
    return _vader.polarity_scores(text)["compound"]


def keyword_severity(text: str) -> str:
    lower = text.lower()
    for label, words in CRISIS_KEYWORDS.items():
        if any(w in lower for w in words):
            return label
    return "NEUTRAL"


def _llm_classify(text: str) -> dict:
    """
    Ask Ollama/phi3:mini to classify the tweet severity.
    Returns dict with keys: label, score, reasoning
    """
    prompt = f"""You are a crisis-monitoring AI. Classify the following tweet by severity level.

Tweet: "{text}"

Respond ONLY with valid JSON (no markdown) in this exact format:
{{"label": "<CRITICAL|HIGH|MEDIUM|LOW|NEUTRAL>", "score": <0.0-1.0>, "reasoning": "<one sentence>"}}"""

    try:
        t0 = time.time()
        resp = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "{}")
        # Strip any accidental markdown fences
        raw = re.sub(r"```[a-z]*", "", raw).strip().strip("`")
        parsed = json.loads(raw)
        parsed["latency_ms"] = round((time.time() - t0) * 1000, 1)
        parsed["source"] = "llm"
        return parsed
    except Exception as exc:
        print(f"[LLM] Fallback to VADER — {exc}")
        return None


def analyze(text: str) -> dict:
    """
    Full analysis pipeline. Returns enriched dict ready for DB insertion.
    """
    vader = vader_score(text)
    keyword = keyword_severity(text)

    # Try LLM first
    llm = _llm_classify(text)

    if llm and llm.get("label") in SEVERITY_LABELS:
        label = llm["label"]
        score = float(llm.get("score", 0.5))
        reasoning = llm.get("reasoning", "")
        source = "llm"
        latency = llm.get("latency_ms", 0)
    else:
        # VADER-based fallback
        if vader <= -0.6 or keyword == "CRITICAL":
            label = "CRITICAL"
            score = abs(vader)
        elif vader <= -0.35 or keyword == "HIGH":
            label = "HIGH"
            score = abs(vader)
        elif vader <= -0.1 or keyword == "MEDIUM":
            label = "MEDIUM"
            score = abs(vader)
        elif vader >= 0.05:
            label = "NEUTRAL"
            score = vader
        else:
            label = "LOW"
            score = abs(vader)
        reasoning = f"VADER fallback — compound={vader:.3f}, keyword={keyword}"
        source = "vader"
        latency = 0

    return {
        "raw_vader": vader,
        "llm_label": label,
        "llm_score": round(score, 3),
        "reasoning": reasoning,
        "analysis_source": source,
        "latency_ms": latency,
    }
