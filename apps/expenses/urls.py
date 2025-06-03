from django.urls import path, include
from rest_framework import routers

from .views import ExpenseNameViewSet, CashInFlowNameViewSet, ExpenseViewSet, CashInFlowViewSet

router = routers.SimpleRouter()
router.register(r'expenses_name', ExpenseNameViewSet, basename='expense_name')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'cash_inflow_name', CashInFlowNameViewSet, basename='cash_inflow_name')
router.register(r'add_money', CashInFlowViewSet, basename='add_money')

urlpatterns = [
    path('', include(router.urls)),
]
