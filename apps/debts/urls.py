from django.urls import path, include
from rest_framework_nested import routers

from .views import DebtViewset, DebtPaymentViewset

router = routers.SimpleRouter()
router.register(r'', DebtViewset)

payment_router = routers.NestedSimpleRouter(router, r'', lookup='debt')
payment_router.register(r'payments', DebtPaymentViewset, basename='debt-payments')


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(payment_router.urls)),
]

