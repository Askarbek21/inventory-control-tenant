from rest_framework import serializers

from .models import *


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store 
        fields = '__all__'


