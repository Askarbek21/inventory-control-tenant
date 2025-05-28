from django_filters import rest_framework as filters
from .models import Measurement, Category, Supplier, Store, Stock, Product
from django import forms

class MeasurementFilter(filters.FilterSet):
    measurement_name = filters.CharFilter(field_name='measurement_name', lookup_expr='icontains')

    class Meta:
        model = Measurement
        fields = '__all__'


class CategoryFilter(filters.FilterSet):
    category_name = filters.CharFilter(field_name='category_name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = '__all__'


class ProductFilter(filters.FilterSet):
    product_name = filters.CharFilter(field_name='product_name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = [
            "color","category","product_name"
        ]

class StockFilter(filters.FilterSet):
    date_of_arrived_gte = filters.DateFilter(
        field_name='date_of_arrived',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_of_arrived_lte = filters.DateFilter(
        field_name='date_of_arrived',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Stock
        exclude = ['history_of_prices',

                   "quantity",
                   "purchase_price_in_us",
                   "purchase_price_in_uz",
                   "exchange_rate",
                   "selling_price",
                   "min_price",
                   "color",
                   ]
