from django_filters import rest_framework as filters
from .models import ExpenseName, CashInFlowName, Expense, CashInFlow
from django import forms


class ExpensesNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ExpenseName
        fields = ['name']


class CashInFlowNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = CashInFlowName
        fields = ['name']


class ExpensesFilter(filters.FilterSet):
    date_gte = filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_lte = filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Expense
        fields = ['store', 'expense_name', 'payment_type', 'date_gte', 'date_lte']


class CashInFlowFilter(filters.FilterSet):
    date_gte = filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_lte = filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = CashInFlow
        fields = ['store', 'cash_inflow_name', 'date_gte', 'date_lte']
