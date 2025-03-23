from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='search_home'),  # Route for search
]