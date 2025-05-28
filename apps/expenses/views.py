from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from config.pagination import CustomPageNumberPagination
from .filters import ExpensesNameFilter, CashInFlowNameFilter, ExpensesFilter, CashInFlowFilter
from .models import ExpenseName, CashInFlowName, Expense, CashInFlow
from .serializers import ExpenseNameSerializer, CashInFlowNameSerializer, ExpenseSerializer, CashInFlowSerializer


class ExpenseNameViewSet(ModelViewSet):
    queryset = ExpenseName.objects.all()
    serializer_class = ExpenseNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesNameFilter


class CashInFlowNameViewSet(ModelViewSet):
    queryset = CashInFlowName.objects.all()
    serializer_class = CashInFlowNameSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CashInFlowNameFilter


class ExpenseViewSet(ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpensesFilter
    pagination_class = CustomPageNumberPagination


class CashInFlowViewSet(ModelViewSet):
    queryset = CashInFlow.objects.all()
    serializer_class = CashInFlowSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CashInFlowFilter
