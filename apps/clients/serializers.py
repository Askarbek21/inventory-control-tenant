from rest_framework import serializers

from apps.staff.serializers import UserSerializer
from .models import Client, BalanceHistory


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client 
        fields = '__all__'
    
    def validate(self, attrs):
        if attrs.get('type') == 'Юр.лицо' and not attrs.get('ceo_name') and not attrs.get('balance'):
            raise serializers.ValidationError('Имя директора и баланс не могут быть пустыми')
        return attrs
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if repr['type'] == 'Физ.лицо':
            repr.pop('ceo_name')
            repr.pop('balance')

        return repr
    
    def update(self, instance, validated_data):
        validated_data.pop('type')
        validated_data.pop('balance')
        return super().update(instance, validated_data)


class BalanceHistorySerializer(serializers.ModelSerializer):
    sale_read = serializers.SerializerMethodField()
    worker_read = UserSerializer(read_only=True, source='worker')

    class Meta:
        model = BalanceHistory
        fields = ['id', 'type', 'sale_read', 'worker_read', 'previous_balance', 'new_balance', 'amount_deducted', 'timestamp']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if repr['type'] == 'Пополнение':
            repr.pop('sale_read')
            repr.pop('amount_deducted')
            
        return repr
    
    def get_sale_read(self, obj):
        from apps.sales.serializers import SaleSerializer
        return SaleSerializer(obj.sale).data

    
class ClientBalanceIncrementSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    