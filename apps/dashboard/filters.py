from django_filters import rest_framework as filters
from apps.items.models import Stock
from django import forms


class StockDashboardFilter(filters.FilterSet):
    class Meta:
        model = Stock
        fields = ['store']