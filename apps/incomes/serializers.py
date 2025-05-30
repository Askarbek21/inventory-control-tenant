from rest_framework import serializers

from apps.stores.serializers import StoreSerializer
from apps.staff.serializers import UserSerializer
from .models import Income


class IncomeSerializer(serializers.ModelSerializer):
    store_read = StoreSerializer(read_only=True, source='store')
    worker_read = UserSerializer(read_only=True, source='worker')
    class Meta:
        model = Income 
        fields = ['id', 'store_read', 'worker_read', 'source', 'description', 'timestamp']