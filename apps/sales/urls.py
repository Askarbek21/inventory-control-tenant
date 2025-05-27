from django.urls import path, include
from rest_framework_nested import routers

from .views import SalePaymentViewset, SaleViewset

router = routers.SimpleRouter()
router.register(r'', SaleViewset)

payment_router = routers.NestedSimpleRouter(router, r'', lookup='sale')
payment_router.register(r'payments', SalePaymentViewset, basename='sale-payments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(payment_router.urls)),
]
