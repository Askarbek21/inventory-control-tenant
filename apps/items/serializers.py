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
    categories_for_recycling = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True,
                                                                  required=False)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category_write', 'category_read', 'measurement', 'color', 'has_color',
                  'history', 'has_kub', 'kub', 'has_recycling', "categories_for_recycling",
                  "is_list",
                  "length",
                  "static_weight",
                  ]

    def create(self, validated_data):
        measurement_data = validated_data.pop('measurementproduct_set')
        categories_for_recycling = validated_data.pop('categories_for_recycling', None)
        product = Product.objects.create(**validated_data)
        category = product.category.category_name
        history = {
            "category": category,
        }
        product.history = history
        if categories_for_recycling:
            product.categories_for_recycling.set(categories_for_recycling)
        product.save()

        for mt in measurement_data:
            MeasurementProduct.objects.create(product=product, **mt)
        return product

    def update(self, instance, validated_data):
        measurement_data = validated_data.pop('measurementproduct_set', [])
        categories_for_recycling = validated_data.pop('categories_for_recycling', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if 'category' in validated_data and validated_data['category']:
            if not instance.history:
                instance.history = {}
            instance.history['category'] = validated_data['category'].category_name

        instance.save()

        if categories_for_recycling is not None:
            instance.categories_for_recycling.set(categories_for_recycling)

        if measurement_data:
            existing_measurements = {
                mp.measurement.id: mp
                for mp in instance.measurementproduct_set.all()
            }

            updated_measurement_ids = []

            for item in measurement_data:
                measurement_id = item['measurement'].id if hasattr(item['measurement'], 'id') else item['measurement']
                number = item.get('number', 0)
                for_sale = item.get('for_sale', False)

                updated_measurement_ids.append(measurement_id)

                if measurement_id in existing_measurements:
                    measurement_product = existing_measurements[measurement_id]
                    measurement_product.number = number
                    measurement_product.for_sale = for_sale
                    measurement_product.save()
                else:
                    MeasurementProduct.objects.create(
                        measurement_id=measurement_id,
                        product=instance,
                        number=number,
                        for_sale=for_sale
                    )

            instance.measurementproduct_set.exclude(
                measurement_id__in=updated_measurement_ids
            ).delete()

        return instance


class CurrencySerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class StockSerializers(ModelSerializer):
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), source='store',
                                                     write_only=True)
    store_read = StoreSerializer(source='store', read_only=True)

    product_write = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                       source='product', write_only=True)

    product_read = ProductSerializer(read_only=True, source='product')

    supplier_read = SuppliersModelSerializer(read_only=True, source='supplier')
    supplier_write = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), write_only=True,
                                                        source='supplier')
    history_of_prices = serializers.JSONField(read_only=True)

    quantity = serializers.FloatField(required=False)
    quantity_for_history = serializers.FloatField(read_only=True)
    purchase_price_in_us = serializers.FloatField(required=False)
    purchase_price_in_uz = serializers.FloatField(required=False)
    exchange_rate_write = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), required=False,
                                                             write_only=True, source='exchange_rate'
                                                             )
    exchange_rate_read = CurrencySerializer(read_only=True, source='exchange_rate')
    selling_price = serializers.FloatField(required=False)
    min_price = serializers.FloatField(required=False)
    date_of_arrived = serializers.DateTimeField()

    class Meta:
        model = Stock
        fields = ['id',
                  'product_write', 'store_write', 'store_read', "product_read", 'purchase_price_in_uz',
                  "purchase_price_in_us",

                  'selling_price', 'exchange_rate_read',
                  'min_price', "exchange_rate_write", 'quantity', 'quantity_for_history',
                  'history_of_prices', 'selling_price_in_us',
                  'supplier_read', 'supplier_write', 'date_of_arrived', 'total_volume',
                  'income_weight'
                  ]

    def create(self, validated_data):
        selling_price = float(validated_data.pop('selling_price', 0))
        min_price = float(validated_data.pop('min_price', 0))
        exchange_rate_write = validated_data.pop('exchange_rate_write', None)
        if exchange_rate_write is None:
            exchange_rate_write = Currency.objects.first()
            if not exchange_rate_write:
                raise serializers.ValidationError("Нет доступной валюты.")
        product_write = validated_data.pop('product', None)
        purchase_price_in_us = validated_data.pop('purchase_price_in_us', None)
        purchase_price_in_uz = float(validated_data.pop('purchase_price_in_uz', 0))
        quantity = float(validated_data.pop('quantity', 0))
        date_of_arrived = validated_data.pop('date_of_arrived', None)
        supplier = validated_data.pop('supplier', None)
        store = validated_data.pop('store', None)
        total_volume = validated_data.pop('total_volume', None)
        product = Product.objects.get(id=product_write.id)

        if product.has_kub and product.kub is not None:
            total_volume = float(quantity) * product.kub
        else:
            total_volume = None

        history = {
            "purchase_price_in_us": purchase_price_in_us,
            "purchase_price_in_uz": purchase_price_in_uz,
            "selling_price": selling_price,
            "min_price": min_price,
            "exchange_rate": f'{exchange_rate_write.currency_rate}',
            "quantity": quantity,
            "total_volume": total_volume,
            "date_of_arrived": f'{date_of_arrived}',
            "supplier": f'{supplier.name} - {supplier.phone_number}',
            "store": f'{store.name} - {store.phone_number}',
        }

        stock = Stock.objects.create(
            **validated_data,
            product=product_write,
            history_of_prices=history,
            selling_price=selling_price,
            min_price=min_price,
            purchase_price_in_us=purchase_price_in_us,
            purchase_price_in_uz=purchase_price_in_uz,
            exchange_rate=exchange_rate_write,
            quantity=quantity,
            quantity_for_history=quantity,
            date_of_arrived=date_of_arrived,
            store=store,
            supplier=supplier,
            total_volume=total_volume,

        )

        return stock

    def update(self, instance, validated_data):
        selling_price = float(validated_data.pop('selling_price', instance.selling_price))
        min_price = float(validated_data.pop('min_price', instance.min_price))

        purchase_price_in_uz = float(validated_data.pop('purchase_price_in_uz', instance.purchase_price_in_uz))
        quantity = float(validated_data.pop('quantity', instance.quantity))

        if instance.product.has_kub and instance.product.kub is not None:
            instance.total_volume = quantity * instance.product.kub
        else:
            instance.total_volume = None

        instance.selling_price = selling_price
        instance.min_price = min_price

        instance.purchase_price_in_uz = purchase_price_in_uz
        instance.quantity = quantity

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
