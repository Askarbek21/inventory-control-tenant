from django.urls import path, include
from rest_framework import routers

from .views import SponsorViewset

router = routers.SimpleRouter()
router.register(r'', SponsorViewset, basename='sponsor')


urlpatterns = [
    path('', include(router.urls)),
]
