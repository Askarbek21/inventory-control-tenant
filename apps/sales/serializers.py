from django.db import transaction
from rest_framework import serializers

from apps.debts.serializers import DebtInSaleSerializer, Debt
from apps.stores.serializers import StoreSerializer
from apps.items.serializers import StockSerializers, MeasurementProduct
from .models import *
from .services import process_sale


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

        if quantity < 0:
            raise serializers.ValidationError('Количество не может быть отрицательным')

        if selling_method == 'Ед.измерения':
            product_measurement = MeasurementProduct.objects.filter(product=product, for_sale=True).first()
            if not product_measurement:
                raise serializers.ValidationError('Измерение с for_sale=True не найдено для продукта')

            if quantity > product_measurement.number:
                raise serializers.ValidationError('Недостаточно измеренного товара')
        else:
            if quantity > stock.quantity:
                raise serializers.ValidationError('Недостаточно товара на складе')
        return attrs


class SalePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayment
        fields = ['amount', 'payment_method']
      

class SaleSerializer(serializers.ModelSerializer):
    sale_items = SaleItemSerializer(many=True, required=False)
    sale_debt = DebtInSaleSerializer(required=False, write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')
    sale_payments = SalePaymentSerializer(many=True, required=False)

    class Meta:
        model = Sale 
        fields = [
            'id', 'store_read', 'client',
            'on_credit', 'sale_items', 'sale_debt',
            'total_amount', 'sale_payments',
            ]
    
    def validate(self, attrs):
        on_credit = attrs.get('on_credit')
        sale_debt = attrs.get('sale_debt')
        client = attrs.get('client', None)

        if on_credit and not sale_debt:
            raise serializers.ValidationError({
                'sale_debt': 'Поле должно быть заполнено'
            })
        
        if client and client.type != 'Юр.лицо':
            raise serializers.ValidationError({
                'client': 'Допускается только юр.лицо'
            })

        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        sale_items = validated_data.pop('sale_items', None)
        sale_debt = validated_data.pop('sale_debt', None)
        sale_payments = validated_data.pop('sale_payments', None)
        total_amount = validated_data.pop('total_amount', None)
        on_credit = validated_data.get('on_credit')

        user = self.context['request'].user
        store = user.store
        
        new_sale = Sale.objects.create(
            store=store,
            sold_by=user,
            **validated_data
        )

        if sale_items is not None:
            item_instances = list()

            for item in sale_items:
                stock = item['stock']
                quantity = item['quantity']
                unit_price = stock.selling_price
                subtotal = item.get('subtotal', quantity*unit_price)

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
            Debt.objects.create(sale=new_sale, store=new_sale.store, total_amount=new_sale.total_amount,**sale_debt)

        if sale_payments is not None:
            payments_lst = [SalePayment(sale=new_sale, **payment) 
            for payment in sale_payments
            ]
            SalePayment.objects.bulk_create(payments_lst)
        
        process_sale(new_sale)

        return new_sale

    def update(self, instance, validated_data):
        validated_data.pop('on_credit', None)
        validated_data.pop('sale_items', None)
        validated_data.pop('sale_debt', None)
        validated_data.pop('sale_payments', None)

        for field,value in validated_data.items():
            if value is not None:
                setattr(instance, field, value)

        instance.save()

        return instance

        



