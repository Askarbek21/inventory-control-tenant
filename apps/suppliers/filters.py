from django_filters import rest_framework as filters
from .models import Supplier


class SupplierFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Supplier
        fields = '__all__'
