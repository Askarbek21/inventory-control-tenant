from django.urls import path, include
from rest_framework_nested import routers

from .views import LoanViewset, LoanPaymentViewset

router = routers.SimpleRouter()
router.register(r'', LoanViewset, basename='loan')

payment_router = routers.NestedSimpleRouter(router, r'', lookup='loan')
payment_router.register(r'payments', LoanPaymentViewset, basename='loan-payments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(payment_router.urls)),
]
