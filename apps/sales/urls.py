from django.urls import path, include
from rest_framework import routers

from .views import SaleViewset

router = routers.SimpleRouter()
router.register(r'', SaleViewset)


urlpatterns = [
    path('', include(router.urls)),
]
