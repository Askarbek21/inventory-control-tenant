from rest_framework import serializers
from django.db import IntegrityError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.stores.serializers import Store, StoreSerializer
from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True, source='store')

    class Meta:
        model = CustomUser 
        fields = ['id', 'name', 'password', 'phone_number', 'role', 'store_read', 'store_write','is_superuser']

    def create(self, validated_data):
        try:
            new_user = CustomUser.objects.create_user(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError('Пользователь с таким номером/именем уже существует!')
        
        return new_user 
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.role = validated_data.get('role', instance.role)
        instance.store = validated_data.get('store', instance.store)
        
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError('Пользователь с таким номером/именем уже существует!')

        return instance
    

#Token
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['phone_number'] = user.phone_number
        token['role'] = user.role
        token['store'] = user.store.id if user.store else None
        token['is_superuser'] = user.is_superuser

        return token
