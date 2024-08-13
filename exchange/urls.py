# exchange/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('rates/', views.ExchangeRate, name='ExchangeRate'),
]
