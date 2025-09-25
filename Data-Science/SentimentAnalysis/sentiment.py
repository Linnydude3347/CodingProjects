from __future__ import annotations
from typing import Iterable

# --- VADER (nltk) ---
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

_DOWNLOADED = False
def _ensure_vader():
    global _DOWNLOADED
    if not _DOWNLOADED:
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
        _DOWNLOADED = True

def analyze_vader(texts: Iterable[str]):
    _ensure_vader()
    sia = SentimentIntensityAnalyzer()
    for t in texts:
        if t is None: t = ""
        s = sia.polarity_scores(t)
        comp = s.get("compound", 0.0)
        if comp >= 0.05:
            label = "positive"
        elif comp <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        yield {"sentiment": label, "sentiment_score": float(comp)}

# --- Transformers (optional) ---
def analyze_hf(texts: Iterable[str], model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("Transformers not installed. Uncomment dependencies in requirements.txt and install.") from e
    clf = pipeline("sentiment-analysis", model=model_name, top_k=None, truncation=True)
    for t in texts:
        if t is None: t = ""
        out = clf(t)[0]
        # Different models may return different labels; normalize
        # Expect labels like: 'LABEL_0','LABEL_1','LABEL_2' or 'negative','neutral','positive'
        label = out.get("label", "").lower()
        score = float(out.get("score", 0.0))
        if label in {"1", "pos", "positive"} or "pos" in label:
            norm = "positive"
        elif label in {"0", "neg", "negative"} or "neg" in label:
            norm = "negative"
        elif label in {"2", "neu", "neutral"} or "neu" in label:
            norm = "neutral"
        else:
            # fallback: map by index if present
            norm = label or "neutral"
        yield {"sentiment": norm, "sentiment_score": score}