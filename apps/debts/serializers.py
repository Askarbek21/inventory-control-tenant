from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.clients.serializers import ClientSerializer
from apps.staff.serializers import UserSerializer
from .models import *


class DebtSerializer(serializers.ModelSerializer):
    sale_read = serializers.SerializerMethodField()
    sale_write = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all(), write_only=True, source='sale')
    client_read = ClientSerializer(read_only=True, source='client')
    client_write = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True, source='client')
    remainder = serializers.SerializerMethodField()
    
    class Meta:
        model = Debt 
        fields = [
            'id', 'sale_read', 'sale_write',
            'client_read', 'client_write',
            'due_date', 'total_amount',
            'deposit', 'is_paid', 'created_at',
            'remainder'
        ]
    
    def validate(self, attrs):
        due_date = attrs.get('due_date')

        if due_date and due_date <= timezone.now().date():
            raise serializers.ValidationError('Некорректная дата')

        return attrs
    
    def get_remainder(self, obj):
        remainder = obj.total_amount - obj.deposit - sum([payment.amount for payment in obj.payments.all()])
        return remainder if remainder > 0 else 0
    
    def get_sale_read(self, obj):
        from apps.sales.serializers import SaleSerializer
        return SaleSerializer(obj.sale).data


class DebtPaymentSerializer(serializers.ModelSerializer):
    worker_read = UserSerializer(read_only=True, source='worker')
    
    class Meta:
        model = DebtPayment
        fields = ['id', 'debt', 'worker_read', 'amount', 'payment_method', 'paid_at']

    def validate(self, attrs):
        debt = attrs.get('debt')

        if debt.is_paid:
            raise serializers.ValidationError("Этот долг уже полностью погашен!")

        return attrs
    
    @transaction.atomic()
    def create(self, validated_data):
        user = self.context['request'].user
        
        new_payment = DebtPayment.objects.create(worker=user, **validated_data)

        return new_payment
    
    def update(self, instance, validated_data):
        validated_data.pop('debt')
        validated_data.pop('amount')
        return super().update(instance, validated_data)


class DebtInSaleSerializer(serializers.ModelSerializer):
    client_read = ClientSerializer(read_only=True, source='client')
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    class Meta:
        model = Debt 
        fields = ['client', 'client_read', 'due_date', 'deposit', 'total_amount']
    
    def validate(self, attrs):
        due_date = attrs.get('due_date')

        if due_date and due_date <= timezone.now().date():
            raise serializers.ValidationError('Некорректная дата')

        return attrs


class ClientDebtSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_deposit = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = Client 
        fields = ['id', 'type', 'name', 'ceo_name', 'phone_number', 'address', 'balance', 'total_amount', 'total_deposit']
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if repr['type'] == 'Физ.лицо':
            repr.pop('ceo_name')
            repr.pop('balance')

        return repr
