from datetime import datetime
from django_filters import rest_framework as filters

from apps.stores.models import Store
from .models import Sale
from django.db.models import Q

class SaleFilter(filters.FilterSet):
    store = filters.ModelChoiceFilter(
        queryset=Store.objects.all(),
        field_name='store',
        to_field_name='id'
    )
    product = filters.CharFilter(method='filter_by_product')
    start_date = filters.DateFilter(method='filter_start_date')
    end_date = filters.DateFilter(method='filter_end_date')
    on_credit = filters.BooleanFilter(field_name='on_credit')

    class Meta:
        model = Sale
        fields = []
    
    def filter_by_product(self, queryset, name, value):
        return queryset.filter(Q(sale_items__stock__product__product_name__icontains=value)).distinct()
    
    def filter_start_date(self, queryset, name, value):
        return queryset.filter(sold_date__gte=datetime.combine(value, datetime.min.time()))

    def filter_end_date(self, queryset, name, value):
        return queryset.filter(sold_date__lte=datetime.combine(value, datetime.max.time()))