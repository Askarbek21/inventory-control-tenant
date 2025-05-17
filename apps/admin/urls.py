from django.urls import path

from .views import UpdateConfigAPIView

urlpatterns = [
    path('', UpdateConfigAPIView.as_view()),
]
