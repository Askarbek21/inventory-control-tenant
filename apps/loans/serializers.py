from rest_framework import serializers
from django.utils import timezone

from apps.sponsors.serializers import SponsorSerializer
from .models import *


class LoanSerializer(serializers.ModelSerializer):
    sponsor_write = serializers.PrimaryKeyRelatedField(queryset=Sponsor.objects.all(), write_only=True)
    sponsor_read = SponsorSerializer(read_only=True)
    remainder = serializers.SerializerMethodField()

    class Meta:
        model = Loan 
        fields = [
            'id', 'sponsor_read', 'sponsor_write', 'is_paid',
            'total_amount', 'currency', 'created_at', 'due_date'
        ]
    
    def validate(self, attrs):
        due_date = attrs.get('due_date')

        if due_date and due_date <= timezone.now().date():
            raise serializers.ValidationError('Некорректная дата')

        return attrs

    def get_remainder(self, obj):
        remainder = obj.total_amount - sum([payment.amount for payment in obj.payments.all()])
        return remainder if remainder > 0 else 0


class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = ['id', 'loan', 'amount', 'notes', 'payment_method', 'paid_at']

    def validate(self, attrs):
        loan = attrs.get('loan')

        if loan.is_paid:
            raise serializers.ValidationError("Этот долг уже полностью погашен!")

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('loan')
        validated_data.pop('amount')
        return super().update(instance, validated_data)