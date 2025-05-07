from django.urls import path, include
from rest_framework import routers

from .views import UserViewset, StaffViewset

router = routers.SimpleRouter()
router.register(r'users', UserViewset)
router.register(r'staff', StaffViewset)

urlpatterns = [
    path('', include(router.urls)),
]

