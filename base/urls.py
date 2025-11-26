from django.urls import path
from . import views

urlpatterns = [
    path('webhook/<platform>/', views.webhook, name='webhook'),
    path("webhook", views.webhook),
]
