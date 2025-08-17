# server/djangoproj/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# React SPA index.html for page routes (GET)
spa = TemplateView.as_view(template_name='index.html')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # --- SPA pages (served by React) ---
    path('', spa, name='home'),                       # "/" shows the app
    path('login/', spa, name='spa_login'),            # "/login" shows login page
    path('register/', spa, name='spa_register'),
    path('about/', spa),
    path('contact/', spa),
    path('dealers/', spa),
    path('dealer/<int:dealer_id>/', spa),
    path('postreview/<int:dealer_id>/', spa),

    # --- API endpoints (Django views) live under /djangoapp/... ---
    # e.g. POST /djangoapp/login ; GET /djangoapp/get_dealers ; etc.
    path('djangoapp/', include('djangoapp.urls')),
]

# static files (fine for the lab env)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
