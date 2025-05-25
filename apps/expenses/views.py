from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from config.pagination import CustomPageNumberPagination
from .filters import ExpensesFilter, CashInFlowNameFilter
from .models import ExpenseName, CashInFlowName, Expense, CashInFlow
from .serializers import ExpenseNameSerializer, CashInFlowNameSerializer, ExpenseSerializer, CashInFlowSerializer


class ExpenseNameViewSet(ModelViewSet):
    queryset = ExpenseName.objects.all()
    serializer_class = ExpenseNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesFilter


class CashInFlowNameViewSet(ModelViewSet):
    queryset = CashInFlowName.objects.all()
    serializer_class = CashInFlowNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CashInFlowNameFilter


class ExpenseViewSet(ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    pagination_class = CustomPageNumberPagination


class CashInFlowViewSet(ModelViewSet):
    queryset = CashInFlow.objects.all()
    serializer_class = CashInFlowSerializer
    pagination_class = CustomPageNumberPagination
