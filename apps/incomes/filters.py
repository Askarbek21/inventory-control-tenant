from django_filters import rest_framework as filters

from config.constants import SOURCE_TYPE_CHOICES
from apps.stores.models import Store
from apps.staff.models import CustomUser
from .models import Income


class IncomeFilter(filters.FilterSet):
    store = filters.ModelChoiceFilter(
        queryset=Store.objects.all(),
        field_name='store',
        to_field_name='id'
    )
    worker = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all(),
        field_name='worker',
        to_field_name='id'
    )
    product_name = filters.CharFilter(
        field_name='sale__sale_items__stock__product__product_name',
        lookup_expr='icontains'
    )
    source = filters.ChoiceFilter(choices=SOURCE_TYPE_CHOICES)
    start_date = filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = Income 
        fields = []