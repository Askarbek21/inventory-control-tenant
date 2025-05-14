from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.suppliers.models import Supplier


class SuppliersModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
