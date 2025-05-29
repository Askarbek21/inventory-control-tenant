from rest_framework import serializers
from apps.items.models import *


class ItemsDashboardSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    date_of_arrived = serializers.DateTimeField()
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    quantity = serializers.IntegerField()
    quantity_for_history = serializers.IntegerField()
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())

    class Meta:
        model = Stock
        fields = ["product", "date_of_arrived",
                  "store",
                  "quantity",
                  "quantity_for_history",
                  "supplier"]
