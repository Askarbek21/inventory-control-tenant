from django_filters import rest_framework as filters
from .models import Store


class StoreFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Store
        fields = ['name']
