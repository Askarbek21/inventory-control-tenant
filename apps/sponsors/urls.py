from django.urls import path, include
from rest_framework_nested import routers

from apps.loans.views import LoanViewset, LoanPaymentViewset
from .views import SponsorViewset

router = routers.SimpleRouter()
router.register(r'', SponsorViewset, basename='sponsor')

loan_router = routers.NestedSimpleRouter(router, r'', lookup='sponsor')
loan_router.register(r'loans', LoanViewset, basename='loan')

payment_router = routers.NestedSimpleRouter(loan_router, r'loans', lookup='loan')
payment_router.register(r'payments', LoanPaymentViewset, basename='loan-payment')


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(loan_router.urls)),
    path(r'', include(payment_router.urls)),
]
