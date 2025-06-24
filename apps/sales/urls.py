from django.urls import path, include
from rest_framework_nested import routers

from .views import SaleViewset, SaleItemViewset, SalePaymentViewset

router = routers.SimpleRouter()
router.register(r'', SaleViewset, basename='sale')

component_router = routers.NestedSimpleRouter(router, r'', lookup='sale')
component_router.register(r'items', SaleItemViewset, basename='sale-items')
component_router.register(r'payments', SalePaymentViewset, basename='sale-payments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(component_router.urls)),
]
