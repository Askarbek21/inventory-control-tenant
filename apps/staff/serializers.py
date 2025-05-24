from rest_framework import serializers
from django.db import IntegrityError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.stores.serializers import StoreSerializer, Store
from .models import *


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64)
    phone_number = serializers.CharField(max_length=13)
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    password = serializers.CharField(write_only=True)

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
        
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError('Пользователь с таким номером/именем уже существует!')

        return instance
    

class StaffSerializer(serializers.ModelSerializer):
    store_read = StoreSerializer(read_only=True, source='store')
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True, source='store')
    user_read = UserSerializer(read_only=True, source='user')
    user_write = UserSerializer(required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False, source='user')
    
    class Meta:
        model = Staff 
        fields = [
            'id', 'store_read', 'store_write',
            'user_read', 'user_write', 'user_id',
            'is_active', 'date_joined'
        ]
    
    def validate(self, attrs):
        user_write = attrs.get('user_write')
        user_id = attrs.get('user_id')
        if not user_write and not user_id:
            raise serializers.ValidationError('Нужен id или данные пользователя')
        if user_write and user_id:
            raise serializers.ValidationError('Некорректный запрос: используйте либо user_id, либо user_write')
        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user_write', None)
        user_id = validated_data.pop('user_id', None)

        if user_data:
            user = CustomUser.objects.create_user(**user_data)
        elif user_id:
            user = user_id

        new_staff = Staff.objects.create(user=user, **validated_data)

        return new_staff
    
    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        validated_data.pop('user_write', None)

        if user_id:
            instance.user = user_id
            
        return super().update(instance, validated_data)

#Token
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['phone_number'] = user.phone_number
        token['role'] = user.role

        return token
