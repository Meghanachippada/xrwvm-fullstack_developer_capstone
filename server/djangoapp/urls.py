from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register', views.registration, name='register'),

    # Cars
    path('get_cars', views.get_cars, name='getcars'),

    # Proxy endpoints to backend
    path('fetchReviews', views.proxy_fetch_reviews),
    path('fetchReviews/dealer/<int:id>', views.proxy_fetch_reviews_by_dealer),
    path('fetchDealers', views.proxy_fetch_dealers),
    path('fetchDealers/<str:state>', views.proxy_fetch_dealers_by_state),
    path('fetchDealer/<int:id>', views.proxy_fetch_dealer_by_id),

    # Dealers (proxy via Django views)
    path(route='get_dealers/', view=views.get_dealerships, name='get_dealers'),
    path('get_dealers', views.get_dealerships, name='get_dealers'),
    path('get_dealers/<str:state>', views.get_dealerships, name='get_dealers_by_state'),

    # Dealer details
    path('dealer/<int:dealer_id>', views.get_dealer_details, name='dealer_details'),
    path('get_dealer/<int:dealer_id>', views.get_dealer_details, name='get_dealer'),  # lab alias

    # Dealer reviews
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews, name='dealer_reviews'),
    path('get_dealer_reviews/<int:dealer_id>', views.get_dealer_reviews, name='get_dealer_reviews'),  # lab alias

    # Add review
    path('add_review', views.add_review, name='add_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
