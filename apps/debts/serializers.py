from rest_framework import serializers

from .models import *


class DebtSerializer(serializers.ModelSerializer):
    remainder = serializers.SerializerMethodField()
    class Meta:
        model = Debt 
        fields = '__all__'
    
    def get_remainder(self, obj):
        remainder = obj.total_amount - obj.deposit - sum([payment.amount for payment in obj.payments.all()])
        return remainder
    

class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = '__all__'
    
    def validate(self, attrs):
        debt = attrs['debt']

        if debt.is_paid:
            raise serializers.ValidationError("Этот долг уже полностью погашен!")

        return attrs
    
    def create(self, validated_data):
        debt = validated_data.get('debt')

        new_payment = super().create(validated_data)
        
        total_paid = debt.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        
        if total_paid >= debt.total_amount:
            debt.is_paid = True
            debt.save(update_fields=['is_paid'])

        return new_payment
    
    def update(self, instance, validated_data):
        validated_data.pop('debt')
        validated_data.pop('amount')
        return super().update(instance, validated_data)


class DebtInSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt 
        fields = ['client', 'due_date']
