from django_filters import rest_framework as filters

from .models import Sale

class SaleFilter(filters.FilterSet):
    product = filters.CharFilter(method='filter_by_product')
    start_date = filters.DateFilter(field_name='sold_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='sold_date', lookup_expr='lte')
    on_credit = filters.BooleanFilter(field_name='on_credit')

    class Meta:
        model = Sale
        fields = []
    
    def filter_by_product(self, queryset, name, value):
        return queryset.filter(sale_items__stock__product__id=value).distinct()