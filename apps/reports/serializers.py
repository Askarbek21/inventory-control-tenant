from rest_framework import serializers


class ProductSalesSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    total_quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

class UnsoldProductSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    last_sold_date = serializers.DateTimeField()

class StockCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    total_stock = serializers.DecimalField(max_digits=12, decimal_places=2)

class ProductIntakeSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_positions = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)

class ProductProfitabilitySerializer(serializers.Serializer):
    product_name = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    margin = serializers.FloatField()

class ClientDebtSerializer(serializers.Serializer):
    client_name = serializers.CharField()
    total_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    deposit = serializers.DecimalField(max_digits=12, decimal_places=2)