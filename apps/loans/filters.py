from django_filters import rest_framework as filters

from config.constants import CURRENCY_CHOICES, PAYMENT_METHOD_CHOICES
from apps.sponsors.models import Sponsor 
from .models import Loan, LoanPayment


class LoanFilter(filters.FilterSet):
    sponsor = filters.ModelChoiceFilter(
        queryset=Sponsor.objects.all(),
        field_name='sponsor',
        to_field_name='id'
    )
    is_paid = filters.BooleanFilter()
    currency = filters.ChoiceFilter(choices=CURRENCY_CHOICES)

    class Meta:
        model = Loan
        fields = []


class LoanPaymentFilter(filters.FilterSet):
    paid_at = filters.DateTimeFromToRangeFilter()
    amount = filters.RangeFilter()
    payment_method = filters.ChoiceFilter(choices=PAYMENT_METHOD_CHOICES)

    class Meta:
        model = LoanPayment
        fields = []