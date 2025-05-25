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
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True)
    user_read = UserSerializer(read_only=True, source='user')
    user_write = UserSerializer(required=False, write_only=True)
        
    class Meta:
        model = Staff 
        fields = '__all__'
    
    def validate(self, attrs):
        user_write = attrs.get('user_write')
        user_id = attrs.get('user')
        if not user_write and not user_id:
            raise serializers.ValidationError('Нужен id или данные пользователя')
        if user_write and user_id:
            raise serializers.ValidationError('Некорректный запрос: используйте либо user_id, либо user_write')
        return attrs

    def create(self, validated_data):
        print(self.initial_data)
        user_data = validated_data.pop('user_write', None)
        if user_data:
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                validated_data['user'] = user
        
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        validated_data.pop('user_write', None)
            
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
