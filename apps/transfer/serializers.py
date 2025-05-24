from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from apps.items.serializers import StockSerializers
from ..items.models import MeasurementProduct
from ..stores.serializers import StoreSerializer


from django.db.models import Q


class TransferSerializer(ModelSerializer):
    from_stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), write_only=True)
    from_stock_read = StockSerializers(source='from_stock', read_only=True)
    to_stock = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True)
    to_stock_read = StoreSerializer(source='to_stock', read_only=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Transfer
        fields = ["from_stock",
                  "to_stock",
                  "stock",
                  "amount",
                  "date_of_transfer",
                  "comment", "to_stock_read", "from_stock_read"
                  ]

    def validate(self, attrs):
        from_stock = attrs['from_stock']
        to_stock = attrs['to_stock']
        amount = attrs['amount']

        if amount > from_stock.quantity or amount <= 0:
            raise ValidationError('Amount must be greater than the quantity in stock.')
        if from_stock.store.id == to_stock.id:
            raise ValidationError('Cannot transfer to the same store.')
        return attrs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('stock')

    def create(self, validated_data):
        from_stock = validated_data.pop('from_stock')
        to_stock = validated_data.pop('to_stock')
        amount = validated_data.pop('amount')

        stock = Stock.objects.get(id=from_stock.id)
        stock.quantity -= float(amount)
        stock.save()

        receiving_stock = Stock.objects.filter(Q(store=to_stock.id) & Q(product=from_stock.product.id)).order_by(
            '-id').first()

        if receiving_stock is None or receiving_stock.quantity == 0:
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
            transfer = Transfer.objects.create(**validated_data,
                                               amount=amount,
                                               from_stock=from_stock,
                                               to_stock=to_stock,
                                               stock=received_stock)
        else:
            receiving_stock.quantity += amount
            receiving_stock.save()
            transfer = Transfer.objects.create(**validated_data,
                                               amount=amount,
                                               from_stock=from_stock,
                                               to_stock=to_stock,
                                               stock=receiving_stock)

        return transfer

    def update(self, instance, validated_data):
        from_stock = instance.from_stock
        stock = instance.stock
        new_amount = validated_data.pop('amount')
        sent_stock = Stock.objects.get(id=from_stock.id)
        got_stock = Stock.objects.get(id=stock.id)

        if instance.amount > new_amount:
            difference = instance.amount - new_amount
            sent_stock.quantity += difference
            got_stock.quantity = new_amount
        elif instance.amount < new_amount:
            difference = new_amount - instance.amount
            sent_stock.quantity -= float(difference)
            got_stock.quantity = new_amount

        sent_stock.save()
        got_stock.save()

        instance.amount = new_amount
        instance.save()
        return instance
