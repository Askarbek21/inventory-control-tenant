from django.forms import model_to_dict
from rest_framework.serializers import ModelSerializer
from apps.items.models import *
from rest_framework import serializers, routers
from apps.stores.serializers import StoreSerializer
from apps.suppliers.serializers import SuppliersModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', ]


class MeasurementSerializer(ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'


class MeasurementProductSerializers(ModelSerializer):
    measurement_write = serializers.PrimaryKeyRelatedField(queryset=Measurement.objects.all(),
                                                           source='measurement', write_only=True)
    measurement_read = MeasurementSerializer(read_only=True, source='measurement', )

    number = serializers.CharField()

    class Meta:
        model = MeasurementProduct
        fields = ['id', 'measurement_write', 'measurement_read', 'number', 'for_sale']


class ProductSerializer(ModelSerializer):
    category_write = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True,
                                                        source='category')
    category_read = CategorySerializer(read_only=True, source='category')
    measurement = MeasurementProductSerializers(many=True, source='measurementproduct_set')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category_write', 'category_read', 'measurement', ]

    def create(self, validated_data):
        measurement_data = validated_data.pop('measurementproduct_set')
        product = Product.objects.create(**validated_data)
        for mt in measurement_data:
            MeasurementProduct.objects.create(product=product, **mt)
        return product

    def update(self, instance, validated_data):
        measurement_data = validated_data.pop('measurementproduct_set')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for item in measurement_data:
            measurement = item['measurement']
            number = item['number']
            for_sale = item['for_sale']

            obj, created = MeasurementProduct.objects.get_or_create(measurement=measurement, product=instance,
                                                                    defaults={'number': number, "for_sale": for_sale})
            if not created:
                obj.number = number
                obj.for_sale = for_sale
                obj.save()

        return instance


class StockSerializers(ModelSerializer):
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.filter(is_main=True), source='store',
                                                     write_only=True)
    store_read = StoreSerializer(source='store', read_only=True)

    product_write = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                       source='product', write_only=True)

    product_read = ProductSerializer(read_only=True, source='product')

    supplier_read = SuppliersModelSerializer(read_only=True, source='supplier')
    supplier_write = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), write_only=True,
                                                        source='supplier')

    quantity = serializers.FloatField(required=False)
    purchase_price_in_us = serializers.FloatField(required=False)
    purchase_price_in_uz = serializers.FloatField(required=False)
    exchange_rate = serializers.FloatField(required=False)
    selling_price = serializers.FloatField(required=False)
    min_price = serializers.FloatField(required=False)
    color = serializers.CharField(required=False)

    class Meta:
        model = Stock
        fields = ['id',
                  'product_write', 'store_write', 'store_read', "product_read", 'purchase_price_in_uz',
                  'purchase_price_in_us',
                  'selling_price',
                  'min_price', "exchange_rate", 'quantity', 'history_of_prices', 'color',
                  'supplier_read', 'supplier_write', 'has_color', 'date_of_arrived'
                  ]

    def create(self, validated_data):
        selling_price = float(validated_data.pop('selling_price', 0))
        min_price = float(validated_data.pop('min_price', 0))
        exchange_rate = float(validated_data.pop('exchange_rate', 0))
        purchase_price_in_us = float(validated_data.pop('purchase_price_in_us', 0))
        purchase_price_in_uz = float(validated_data.pop('purchase_price_in_uz', 0))
        quantity = float(validated_data.pop('quantity', 0))

        history = {
            "purchase_price_in_us": purchase_price_in_us,
            "purchase_price_in_uz": purchase_price_in_uz,
            "selling_price": selling_price,
            "min_price": min_price,
            "exchange_rate": exchange_rate,
            "quantity": quantity,
        }

        stock = Stock.objects.create(
            **validated_data,
            history_of_prices=history,
            selling_price=selling_price,
            min_price=min_price,
            purchase_price_in_us=purchase_price_in_us,
            purchase_price_in_uz=purchase_price_in_uz,
            exchange_rate=exchange_rate,
            quantity=quantity
        )

        return stock

    def update(self, instance, validated_data):
        selling_price = float(validated_data.pop('selling_price', instance.selling_price))
        min_price = float(validated_data.pop('min_price', instance.min_price))
        exchange_rate = float(validated_data.pop('exchange_rate', instance.exchange_rate))
        purchase_price_in_us = float(validated_data.pop('purchase_price_in_us', instance.purchase_price_in_us))
        purchase_price_in_uz = float(validated_data.pop('purchase_price_in_uz', instance.purchase_price_in_uz))
        quantity = float(validated_data.pop('quantity', instance.quantity))

        instance.selling_price = selling_price
        instance.min_price = min_price
        instance.exchange_rate = exchange_rate
        instance.purchase_price_in_us = purchase_price_in_us
        instance.purchase_price_in_uz = purchase_price_in_uz
        instance.quantity = quantity

        history = {
            "purchase_price_in_us": purchase_price_in_us,
            "purchase_price_in_uz": purchase_price_in_uz,
            "selling_price": selling_price,
            "min_price": min_price,
            "exchange_rate": exchange_rate,
            "quantity": quantity,
        }
        instance.history_of_prices = history

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
