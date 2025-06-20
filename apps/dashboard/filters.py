from django_filters import rest_framework as filters
from apps.items.models import Stock
from django import forms


class StockDashboardFilter(filters.FilterSet):
    product_zero = filters.BooleanFilter(method='check_product_zero', )

    def check_product_zero(self, queryset, name, value):
        if value:
            return queryset.filter(quantity=0)
        return queryset.filter(quantity__gt=0)

    class Meta:
        model = Stock
        fields = ['store', 'product_zero']
