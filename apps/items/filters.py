from django_filters import rest_framework as filters
from .models import Measurement, Category, Supplier, Store, Stock, Product


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
        fields = '__all__'


class StockFilter(filters.FilterSet):
    date_of_arrived_gte = filters.DateTimeFilter(field_name='date_of_arrived', lookup_expr='gte', )
    date_of_arrived_lte = filters.DateTimeFilter(field_name='date_of_arrived', lookup_expr='lte', )

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
