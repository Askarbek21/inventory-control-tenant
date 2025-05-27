from django.core.validators import MinValueValidator
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.items.models import Stock, Product
from apps.items.serializers import StockSerializers, ProductSerializer
from apps.recycling.models import Recycling

from apps.stores.models import Store


class RecyclingSerializer(ModelSerializer):
    from_to = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), write_only=True)
    to_product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    purchase_price_in_us = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    purchase_price_in_uz = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    exchange_rate = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    selling_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    min_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True)
    spent_amount = serializers.FloatField(validators=[MinValueValidator(0)]
                                          )
    get_amount = serializers.FloatField(validators=[MinValueValidator(0)])
    to_stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), required=False, write_only=True)

    from_to_read = StockSerializers(source='from_to', read_only=True)
    to_product_read = ProductSerializer(source='to_product', read_only=True)
    to_stock_read = StockSerializers(source='to_stock', read_only=True)

    class Meta:
        model = Recycling
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.method == 'POST':
            self.fields.pop('to_stock')

    def create(self, validated_data):
        from_to = validated_data.pop('from_to')
        to_product = validated_data.pop('to_product')

        spent_amount = validated_data.pop('spent_amount')
        get_amount = validated_data.pop('get_amount')
        purchase_price_in_us = float(validated_data.pop('purchase_price_in_us', 0))
        purchase_price_in_uz = float(validated_data.pop('purchase_price_in_uz', 0))
        exchange_rate = float(validated_data.pop('exchange_rate', 0))
        selling_price = float(validated_data.pop('selling_price', 0))
        min_price = float(validated_data.pop('min_price', 0))

        store = validated_data.pop('store')

        stock = Stock.objects.get(id=from_to.id)
        if spent_amount > stock.quantity:
            raise serializers.ValidationError('spent amount exceeds stock quantity')
        else:
            stock.quantity -= spent_amount
        stock.save()

        history = {
            "purchase_price_in_us": purchase_price_in_us,
            "purchase_price_in_uz": purchase_price_in_uz,
            "exchange_rate": exchange_rate,
            "selling_price": selling_price,
            "min_price": min_price,

        }

        recycled_product_in_stock = Stock.objects.create(
            product=to_product,
            purchase_price_in_us=purchase_price_in_us,
            purchase_price_in_uz=purchase_price_in_uz,
            exchange_rate=exchange_rate,
            selling_price=selling_price,
            min_price=min_price,

            history_of_prices=history,
            quantity=get_amount,
            store=store
        )

        recycled_product = Recycling.objects.create(
            from_to=from_to,
            to_product=to_product,
            spent_amount=spent_amount,
            get_amount=get_amount,
            to_stock=recycled_product_in_stock
        )

        return recycled_product

    def update(self, instance, validated_data):
        from_to = validated_data.pop('from_to')
        to_stock = validated_data.pop('to_stock')
        spent_amount = validated_data.pop('spent_amount', instance.spent_amount)

        update_from_stock = Stock.objects.get(id=from_to.id)

        if spent_amount > update_from_stock.quantity:
            raise serializers.ValidationError('spent amount exceeds stock quantity')
        elif spent_amount > instance.spent_amount:
            difference = spent_amount - instance.spent_amount
            update_from_stock.quantity -= difference
            update_from_stock.save()
        elif spent_amount < instance.spent_amount:
            difference = instance.spent_amount - spent_amount
            update_from_stock.quantity += difference
            update_from_stock.save()

        update_to_stock = Stock.objects.get(id=to_stock.id)
        update_to_stock.quantity = validated_data.get('get_amount', instance.get_amount)
        update_to_stock.save()

        instance.spent_amount = spent_amount
        instance.get_amount = validated_data.get('get_amount', instance.get_amount)
        instance.save()

        return instance
