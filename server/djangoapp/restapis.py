# restapis.py
import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# lower-case keys as per your project
backend_url = os.getenv("backend_url", "http://localhost:3000").rstrip("/")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050/"
).rstrip("/") + "/"

def get_request(endpoint: str, **kwargs):
    """
    Simple GET wrapper to your Node backend.
    Returns [] on failure so templates don't break.
    """
    try:
        endpoint = str(endpoint).lstrip("/")
        url = f"{backend_url}/{endpoint}"
        print(f"GET from {url}")
        resp = requests.get(url, params=kwargs or None, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return []  # Django views expect iterable/JSON

def analyze_review_sentiments(text: str):
    """
    Calls the sentiment analyzer service.
    Returns {'sentiment': 'neutral'} on failure.
    """
    try:
        safe = quote_plus(str(text or ""))
        url = sentiment_analyzer_url + "analyze/" + safe
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Sentiment call failed: {e}")
        return {"sentiment": "neutral"}

def post_review(data_dict: dict):
    """
    Posts a review to the Node backend.
    """
    try:
        url = backend_url + "/insert_review"
        resp = requests.post(url, json=data_dict, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"post_review error: {e}")
        return {"status": 500, "message": "Backend insert failed"}
