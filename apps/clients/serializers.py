from django.db.models import Q
from rest_framework import serializers

from apps.staff.serializers import UserSerializer
from apps.stores.models import Store
from .models import Client, BalanceHistory


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone_number = serializers.CharField()
    stores = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), many=True, write_only=True, required=False)
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
    
    def create(self, validated_data):
        name = validated_data.get('name')
        phone = validated_data.get('phone_number')
        store = self.context['request'].user.store

        client = Client.objects.filter(Q(name=name) | Q(phone_number=phone)).first()
        if client:
            client.stores.add(store)
            return client

        client = super().create(validated_data)
        client.stores.add(store)
        return client
    
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
    