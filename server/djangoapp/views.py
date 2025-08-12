# Uncomment the required imports before adding the code

from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data['userName']
            password = data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
            else:
                return JsonResponse({"message": "The user could not be authenticated."}, status=401)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({"message": "Invalid request format."}, status=400)
    else:
        return JsonResponse({"message": "Only POST requests are allowed."}, status=405)


@csrf_exempt
def logout_user(request):
    logout(request)  # Terminate the user session
    data = {"userName": ""}  # Return empty username to clear frontend state
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data["userName"]
        password = data["password"]
        first_name = data["firstName"]
        last_name = data["lastName"]
        email = data["email"]

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Already Registered"})
        else:
            user = User.objects.create_user(username=username, password=password,
                                            first_name=first_name, last_name=last_name, email=email)
            login(request, user)
            return JsonResponse({"userName": username, "status": True})

def get_cars(request):
    count = CarMake.objects.all().count()
    print("CarMake count:", count)
    if count == 0:
        print("Calling initiate() to populate the DB...")
        initiate()
    
    car_models = CarModel.objects.select_related('car_make').all()
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...

def proxy_fetch_reviews(request):
    # all reviews
    data = get_request("fetchReviews")
    return JsonResponse(data, safe=False)

def proxy_fetch_reviews_by_dealer(request, id):
    data = get_request(f"fetchReviews/dealer/{id}")
    return JsonResponse(data, safe=False)

def proxy_fetch_dealers(request):
    data = get_request("fetchDealers")
    return JsonResponse(data, safe=False)

def proxy_fetch_dealers_by_state(request, state):
    data = get_request(f"fetchDealers/{state}")
    return JsonResponse(data, safe=False)

def proxy_fetch_dealer_by_id(request, id):
    data = get_request(f"fetchDealer/{id}")
    return JsonResponse(data, safe=False)

# List dealerships: all or by state
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint) or []
    return JsonResponse({"status": 200, "dealers": dealerships})

# Single dealer by id
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint) or {}
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})

def get_dealer_reviews(request, dealer_id: int):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint) or []

    enriched = []
    for r in reviews:
        text = r.get("review", "")
        senti = analyze_review_sentiments(text)
        # accept either {"sentiment": "..."} or {"label": "..."} shapes
        sentiment_value = (
            senti.get("sentiment")
            or senti.get("label")
            or "neutral"
        )
        r["sentiment"] = sentiment_value
        enriched.append(r)

    return JsonResponse({"status": 200, "reviews": enriched})

@csrf_exempt
@require_http_methods(["POST"])
def add_review(request):
    # Only logged-in users can post
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"}, status=403)

    # Parse body
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"status": 400, "message": "Invalid JSON body"}, status=400)

    # (Optional) Basic field validation to prevent empty inserts
    required = ["dealership", "name", "review", "purchase"]
    missing = [k for k in required if k not in payload]
    if missing:
        return JsonResponse(
            {"status": 400, "message": f"Missing required fields: {', '.join(missing)}"},
            status=400,
        )

    # Forward to backend
    try:
        backend_resp = post_review(payload)  # dict from Node backend
        # Normalize success for the lab rubric
        return JsonResponse({"status": 200, "result": backend_resp}, status=200)
    except Exception as e:
        return JsonResponse(
            {"status": 500, "message": f"Error in posting review: {str(e)}"},
            status=500,
        )
