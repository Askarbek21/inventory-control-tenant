from django.db.models import Q
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from apps.items.serializers import StockSerializers
from ..items.models import MeasurementProduct


class TransferSerializer(ModelSerializer):
    from_stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    to_stock = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Transfer
        fields = '__all__'

    def validate(self, attrs):
        from_stock = attrs['from_stock']
        to_stock = attrs['to_stock']
        amount = attrs['amount']

        if amount > from_stock.quantity or amount <= 0:
            raise ValidationError('Amount must be greater than the quantity in stock.')
        if from_stock.store.id == to_stock.id:
            raise ValidationError('Cannot transfer to the same store.')
        return attrs

    def create(self, validated_data):
        from_stock = validated_data.pop('from_stock')
        to_stock = validated_data.pop('to_stock')
        amount = validated_data.pop('amount')
        transfer = Transfer.objects.create(**validated_data,
                                           amount=amount,
                                           from_stock=from_stock,
                                           to_stock=to_stock
                                           )
        stock = Stock.objects.get(id=from_stock.id)
        stock.quantity -= amount
        stock.save()
        try:
            receiving_stock = Stock.objects.get(Q(store=to_stock.id) & Q(product=from_stock.product.id))
            if receiving_stock.quantity == 0:
                received_stock = Stock.objects.create(
                    store=to_stock,
                    quantity=amount,
                    product=stock.product,
                    purchase_price_in_us=stock.purchase_price_in_us,
                    purchase_price_in_uz=stock.purchase_price_in_uz,
                    selling_price=stock.selling_price,
                    min_price=stock.min_price,
                    exchange_rate=stock.exchange_rate,
                    history_of_prices=stock.history_of_prices,
                    color=stock.color,
                    supplier=stock.supplier,
                )

                received_stock.save()
            else:
                receiving_stock.quantity += amount
                receiving_stock.save()
        except Stock.DoesNotExist:
            received_stock = Stock.objects.create(
                store=to_stock,
                quantity=amount,
                product=stock.product,
                purchase_price_in_us=stock.purchase_price_in_us,
                purchase_price_in_uz=stock.purchase_price_in_uz,
                selling_price=stock.selling_price,
                min_price=stock.min_price,
                exchange_rate=stock.exchange_rate,
                history_of_prices=stock.history_of_prices,
                color=stock.color,
                supplier=stock.supplier,
            )

            received_stock.save()

        return transfer
