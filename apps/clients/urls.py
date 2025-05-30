from django.urls import path, include, re_path
from rest_framework import routers

from .views import ClientViewset, ClientBalanceHistoryView

router = routers.SimpleRouter()
router.register(r'', ClientViewset, basename='client')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'(?P<client_pk>[^/.]+)/history', ClientBalanceHistoryView.as_view()),
]
