from django.urls import path, include
from rest_framework import routers

from .views import ClientViewset

router = routers.SimpleRouter()
router.register(r'', ClientViewset)

urlpatterns = [
    path('', include(router.urls)),
]
