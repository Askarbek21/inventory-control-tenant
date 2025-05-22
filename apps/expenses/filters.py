from django_filters import rest_framework as filters
from .models import ExpenseName, CashInFlowName


class ExpensesFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ExpenseName
        fields = ['name']


class CashInFlowNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = CashInFlowName
        fields = ['name']
