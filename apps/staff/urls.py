from django.urls import path, include
from rest_framework import routers

from .views import UserViewset

router = routers.SimpleRouter()
router.register(r'', UserViewset, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]

