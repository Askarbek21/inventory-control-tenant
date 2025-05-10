from rest_framework import serializers

from apps.items.models import *
from apps.stores.serializers import StoreSerializer


class CategorySerializer(serializers.ModelSerializer):
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.filter(is_main=True), source='store',
                                                     write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'store_write', 'store_read']


class ProductSerializer(serializers.ModelSerializer):
    category_write = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True,
                                                        source='category')
    category_read = CategorySerializer(read_only=True, source='category')

    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.filter(is_main=True), source='store',
                                                     write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category_write', 'category_read', 'store_write', 'store_read']


class MeasurementSerializer(serializers.ModelSerializer):
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.filter(is_main=True), source='store',
                                                     write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')

    class Meta:
        model = Measurement
        fields = ['id', 'measurement_name', 'store_write', 'store_read']


class MeasurementArrivedProductInStoreSerializers(serializers.ModelSerializer):
    measurement_write = serializers.PrimaryKeyRelatedField(queryset=Measurement.objects.filter(store__is_main=True),
                                                           source='measurement', )
    measurement_read = MeasurementSerializer(read_only=True, source='measurement')

    class Meta:
        model = MeasurementArrivedProductInStore
        fields = ['id', 'measurement_write', 'measurement_read', "number"]


class StockSerializers(serializers.ModelSerializer):
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.filter(is_main=True), source='store',
                                                     write_only=True)
    product_write = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(store__is_main=True),
                                                       source='product', write_only=True)

    product_read = ProductSerializer(read_only=True, source='product')

    measurement_write = MeasurementArrivedProductInStoreSerializers(many=True, write_only=True)
    measurement_read = MeasurementArrivedProductInStoreSerializers(many=True, read_only=True,
                                                                   source='measurementarrivedproductinstore_set')

    class Meta:
        model = Stock
        fields = ['id',
                  'product_write', 'store_write', "product_read", 'purchase_price', 'selling_price',
                  'min_price', 'measurement_write', 'measurement_read', 'quantity',
                  ]

    def create(self, validated_data):
        measurement_write = validated_data.pop('measurement_write')
        stock = Stock.objects.create(**validated_data)
        for item in measurement_write:
            MeasurementArrivedProductInStore.objects.create(
                stock=stock,
                measurement=item['measurement'],
                number=item['number'],
            )

        return stock

    def update(self, instance, validated_data):
        measurement_write = validated_data.pop('measurement_write')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.measurementarrivedproductinstore_set.all().delete()

        for item in measurement_write:
            MeasurementArrivedProductInStore.objects.create(
                stock=instance,
                measurement=item['measurement'],
                number=item['number'],

            )

        return instance
