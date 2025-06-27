from django_filters import rest_framework as filters
from .models import Transfer


class TransferFilter(filters.FilterSet):
    product_name = filters.CharFilter(field_name='from_stock__product__product_name', lookup_expr='icontains')

    class Meta:
        model = Transfer
        fields = ['from_stock', ]
