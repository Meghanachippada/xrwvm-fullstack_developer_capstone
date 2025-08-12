# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # # path for registration

    # path for login
    path(route='login', view=views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path("register", views.registration, name="register"),
    path('get_cars', views.get_cars, name='getcars'),
    path('fetchReviews', views.proxy_fetch_reviews),
    path('fetchReviews/dealer/<int:id>', views.proxy_fetch_reviews_by_dealer),

    path('fetchDealers', views.proxy_fetch_dealers),
    path('fetchDealers/<str:state>', views.proxy_fetch_dealers_by_state),
    path('fetchDealer/<int:id>', views.proxy_fetch_dealer_by_id),

    # path for dealer reviews view

    # path for add a review view

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
