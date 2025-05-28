from django.urls import path

from .views import IncomeView

urlpatterns = [
    path('', IncomeView.as_view()),
]
