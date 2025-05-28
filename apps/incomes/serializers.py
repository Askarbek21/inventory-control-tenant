from rest_framework import serializers

from apps.stores.serializers import StoreSerializer
from .models import Income


class IncomeSerializer(serializers.ModelSerializer):
    store_read = StoreSerializer(read_only=True, source='store')
    class Meta:
        model = Income 
        fields = ['id', 'store_read', 'source', 'description', 'timestamp']