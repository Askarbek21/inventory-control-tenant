from django_filters import rest_framework as filters

from config.constants import SOURCE_TYPE_CHOICES
from apps.stores.models import Store
from .models import Income


class IncomeFilter(filters.FilterSet):
    store = filters.ModelChoiceFilter(
        queryset=Store.objects.all(),
        field_name='store',
        to_field_name='id'
    )
    source = filters.ChoiceFilter(choices=SOURCE_TYPE_CHOICES)
    start_date = filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = Income 
        fields = []