from django.urls import path, include
from rest_framework import routers

from .views import *

# router = routers.DefaultRouter()
# router.register

urlpatterns = [
    path('item_dashboard/', ItemsDashboardAPIView.as_view(), ),
    path('excel_export/', ExportExcelAPIView.as_view(), ),
]
