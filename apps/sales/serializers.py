from django.db import transaction
from rest_framework import serializers

from apps.debts.serializers import DebtInSaleSerializer, Debt
from apps.stores.serializers import StoreSerializer
from apps.items.serializers import StockSerializers, MeasurementProduct
from .models import *


class SaleItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    stock_read = StockSerializers(read_only=True, source='stock')
    stock_write = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), write_only=True, source='stock')
    class Meta:
        model = SaleItem
        fields = ['id', 'stock_read', 'stock_write','quantity', 'selling_method', 'subtotal']
    
    def validate(self, attrs):
        stock = attrs['stock']
        quantity = attrs['quantity']
        selling_method = attrs['selling_method']
        product = stock.product
        product_measurement = MeasurementProduct.objects.get(product=product, for_sale=True)

        if quantity < 0:
            raise serializers.ValidationError('Количество не может быть отрицательным')

        if selling_method == 'Ед.измерения':
            product_measurement = MeasurementProduct.objects.get(product=product, for_sale=True)
            if not product_measurement:
                raise serializers.ValidationError('Измерение с for_sale=True не найдено для продукта')

            if quantity > product_measurement.number:
                raise serializers.ValidationError('Недостаточно измеренного товара')
        else:
            if quantity > stock.quantity:
                raise serializers.ValidationError('Недостаточно товара на складе')


class SaleSerializer(serializers.ModelSerializer):
    sale_items = SaleItemSerializer(many=True, required=False)
    sale_debt = DebtInSaleSerializer(required=False, write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')
    store_write = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True, source='store')

    class Meta:
        model = Sale 
        fields = [
            'id', 'store_read', 'payment_method', 
            'on_credit', 'sale_items', 'sale_debt',
            'total_amount', 'store_write'
            ]
    
    def validate(self, attrs):
        on_credit = attrs.get('on_credit')
        sale_debt = attrs.get('sale_debt')

        if on_credit and not sale_debt:
            raise serializers.ValidationError({
                'sale_debt': 'Поле должно быть заполнено'
            })
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        sale_items = validated_data.pop('sale_items', None)
        sale_debt = validated_data.pop('sale_debt', None)
        total_amount = validated_data.pop('total_amount', None)
        on_credit = validated_data.get('on_credit')
        
        new_sale = Sale.objects.create(
            sold_by=self.context['request'].user,
            **validated_data
        )

        if sale_items is not None:
            item_instances = list()

            for item in sale_items:
                stock = item['stock']
                quantity = item['quantity']
                unit_price = stock.selling_price
                subtotal = quantity * unit_price

                item_instances.append(SaleItem(
                    sale=new_sale,
                    stock=stock,
                    quantity=quantity,
                    selling_method=item['selling_method'],
                    subtotal=subtotal,
                ))
            
            SaleItem.objects.bulk_create(item_instances)
        
        new_sale.total_amount = total_amount if total_amount else new_sale.get_total_amount()
        new_sale.save()

        if on_credit:
            Debt.objects.create(sale=new_sale, total_amount=new_sale.total_amount,**sale_debt)

        return new_sale

    def update(self, instance, validated_data):
        on_credit = validated_data.pop('on_credit')
        sale_items = validated_data.pop('sale_items', None)
        sale_debt = validated_data.pop('sale_debt', None)

        for field,value in validated_data.items():
            if value is not None:
                setattr(instance, field, value)

        instance.save()

        



