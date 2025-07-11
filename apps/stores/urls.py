from django.urls import path, include
from rest_framework import routers

from .views import StoreViewset

router = routers.SimpleRouter()
router.register(r'', StoreViewset, basename='store')

urlpatterns = [
    path('', include(router.urls)),
]
