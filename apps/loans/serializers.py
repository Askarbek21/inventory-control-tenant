from rest_framework import serializers
from django.utils import timezone

from apps.sponsors.serializers import SponsorSerializer
from apps.loans.services import apply_existing_overpayment, apply_loan_payment
from .models import *


class LoanSerializer(serializers.ModelSerializer):
    sponsor_write = serializers.PrimaryKeyRelatedField(queryset=Sponsor.objects.all(), write_only=True,source='sponsor')
    sponsor_read = SponsorSerializer(read_only=True, source='sponsor')
    remainder = serializers.DecimalField(max_digits=20, decimal_places=2, source='remaining_balance', read_only=True)
    overpayment_unused = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Loan 
        fields = [
            'id', 'sponsor_read', 'sponsor_write', 'is_paid',
            'total_amount', 'currency', 'created_at', 'due_date',
            'remainder', 'overpayment_unused'
        ]
    
    def validate(self, attrs):
        due_date = attrs.get('due_date')

        if due_date and due_date <= timezone.now().date():
            raise serializers.ValidationError('Некорректная дата')

        return attrs

    def create(self, validated_data):
        new_loan = super().create(validated_data)
        apply_existing_overpayment(new_loan)
        return new_loan
    
    def update(self, instance, validated_data):
        validated_data.pop('total_amount', None)
        validated_data.pop('currency', None)
        return super().update(instance, validated_data)


class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = ['id', 'loan', 'amount', 'notes', 'payment_method', 'paid_at']

    def validate(self, attrs):
        loan = attrs.get('loan')

        if loan.is_paid:
            raise serializers.ValidationError("Этот долг уже полностью погашен!")

        return attrs
    
    def create(self, validated_data):
        return apply_loan_payment(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('loan')
        validated_data.pop('amount')
        return super().update(instance, validated_data)
