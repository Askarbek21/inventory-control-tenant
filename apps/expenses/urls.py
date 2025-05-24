from django.urls import path, include
from rest_framework import routers

from .views import ExpenseNameViewSet, CashInFlowNameViewSet, ExpenseViewSet

router = routers.SimpleRouter()
router.register(r'expenses_name', ExpenseNameViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'cash_inflow_name', CashInFlowNameViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
