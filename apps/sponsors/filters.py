from django_filters import rest_framework as filters

from .models import Sponsor


class SponsorFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Sponsor 
        fields = ['name']