from django_filters import rest_framework as filters
from .models import *
from django import forms


class RecyclingFilter(filters.FilterSet):
    stock_id = filters.NumberFilter(field_name="from_to")

    class Meta:
        model = Recycling
        fields = ['stock_id']
