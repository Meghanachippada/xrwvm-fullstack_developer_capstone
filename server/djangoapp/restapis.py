# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus


load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# def get_request(endpoint, **kwargs):
# Add code for get requests to back end

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments

# def post_review(data_dict):
# Add code for posting review
def get_request(endpoint, **kwargs):
    # Ensure no duplicate slashes
    endpoint = endpoint.lstrip('/')
    base_url = backend_url.rstrip('/')
    
    # Build full request URL
    request_url = f"{base_url}/{endpoint}"
    
    # Append query params if provided
    if kwargs:
        from urllib.parse import urlencode
        request_url += "?" + urlencode(kwargs)
    
    print(f"GET from {request_url}")
    
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()  # Raises HTTPError if not 200
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        return None

def analyze_review_sentiments(text):
    safe = quote_plus(str(text))
    request_url = sentiment_analyzer_url + "analyze/" + safe
    try:
        response = requests.get(request_url, timeout=10)
        return response.json()
    except Exception as err:
        print(f"Sentiment call failed: {err}")
        return {"sentiment": "neutral"}


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"post_review error: {err}")
        return {"status": 500, "message": "Backend insert failed"}
