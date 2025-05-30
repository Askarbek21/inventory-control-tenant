from django_filters import rest_framework as filters

from config.constants import CLIENT_TYPE_CHOICES, BALANCE_HISTORY_TYPE_CHOICES
from apps.sales.models import Sale
from apps.staff.models import CustomUser
from .models import Client, BalanceHistory


class ClientFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=CLIENT_TYPE_CHOICES)

    class Meta:
        model = Client 
        fields = ['type']


class ClientBalanceFilter(filters.FilterSet):
    sale = filters.ModelChoiceFilter(
        queryset=Sale.objects.all(),
        field_name='sale',
        to_field_name='id'
    )
    worker = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all(),
        field_name='worker',
        to_field_name='id'
    )
    type = filters.ChoiceFilter(choices=BALANCE_HISTORY_TYPE_CHOICES)
    start_date = filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = BalanceHistory
        fields = []