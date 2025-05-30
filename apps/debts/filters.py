from django_filters import rest_framework as filters

from apps.stores.models import Store
from apps.clients.models import Client
from apps.staff.models import CustomUser

from config.constants import PAYMENT_METHOD_CHOICES
from .models import Debt, DebtPayment


class DebtFilter(filters.FilterSet):
    store = filters.ModelChoiceFilter(
        queryset=Store.objects.all(),
        field_name='store',
        to_field_name='id'
    )
    client = filters.ModelChoiceFilter(
        queryset=Client.objects.all(),
        field_name='client',
        to_field_name='id'
    )
    due_date = filters.DateFromToRangeFilter()
    is_paid = filters.BooleanFilter()
    created_at = filters.DateTimeFromToRangeFilter()
    total_amount = filters.RangeFilter()

    class Meta:
        model = Debt
        fields = []


class DebtPaymentFilter(filters.FilterSet):
    paid_at = filters.DateTimeFromToRangeFilter()
    amount = filters.RangeFilter()
    payment_method = filters.ChoiceFilter(choices=PAYMENT_METHOD_CHOICES)
    worker = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all(),
        field_name='worker',
        to_field_name='id'
    )

    class Meta:
        model = DebtPayment
        fields = []