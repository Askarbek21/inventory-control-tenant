# from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from apps.staff.views import CustomTokenObtainPairView

urlpatterns = [
    #    path('admin/', admin.site.urls),



]
