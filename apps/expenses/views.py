from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from config.pagination import CustomPageNumberPagination
from config.permissions import ExpensePermission, IsAdministrator
from .filters import ExpensesNameFilter, CashInFlowNameFilter, ExpensesFilter, CashInFlowFilter
from .models import ExpenseName, CashInFlowName, Expense, CashInFlow
from .serializers import ExpenseNameSerializer, CashInFlowNameSerializer, ExpenseSerializer, CashInFlowSerializer


class ExpenseNameViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdministrator]
    queryset = ExpenseName.objects.all()
    serializer_class = ExpenseNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesNameFilter


class CashInFlowNameViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdministrator]
    queryset = CashInFlowName.objects.all()
    serializer_class = CashInFlowNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CashInFlowNameFilter


class ExpenseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ExpensePermission]
    serializer_class = ExpenseSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(store=self.request.user.store)
    

class CashInFlowViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ExpensePermission]
    serializer_class = CashInFlowSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CashInFlowFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CashInFlow.objects.all()
        return CashInFlow.objects.filter(store=self.request.user.store)
