from django.db import transaction
from rest_framework import serializers

from apps.debts.serializers import DebtInSaleSerializer, Debt
from apps.stores.serializers import StoreSerializer
from apps.items.serializers import StockSerializers, MeasurementProduct
from apps.staff.serializers import UserSerializer
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
            
            meters_per_piece = float(product_measurement.number)
            available_meters = stock.quantity * meters_per_piece

            if quantity > available_meters:
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
    sale_items = SaleItemSerializer(many=True)
    sale_debt = DebtInSaleSerializer(required=False, write_only=True)
    store_read = StoreSerializer(read_only=True, source='store')
    worker_read = UserSerializer(read_only=True, source='sold_by')
    sale_payments = SalePaymentSerializer(many=True, required=False)
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True, required=False)
    sold_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True, required=False)

    class Meta:
        model = Sale 
        fields = [
            'id', 'store_read', 'worker_read', 'client', 'store', 'sold_by',
            'on_credit', 'sale_items', 'sale_debt',
            'total_amount', 'sale_payments', 'is_paid',
            ]
    
    def validate(self, attrs):
        on_credit = attrs.get('on_credit')
        sale_debt = attrs.get('sale_debt')
        client = attrs.get('client', None)
        sale_payments = attrs.get('sale_payments', None)
        store = attrs.get('store', None)
        sold_by = attrs.get('sold_by', None)
        deposit = sale_debt.get('deposit', None)
        total_amount = attrs.get('total_amount', None)

        if on_credit and not sale_debt:
            raise serializers.ValidationError({
                'sale_debt': 'Поле должно быть заполнено'
            })
        
        if client and client.type != 'Юр.лицо':
            raise serializers.ValidationError({
                'client': 'Допускается только юр.лицо'
            })
        
        if not on_credit and not sale_payments and not client:
            raise serializers.ValidationError({
                'sale_payments': 'Поле должно быть заполнено'
            })
        
        if sold_by and store and sold_by.store != store:
            raise serializers.ValidationError({
                'Данный работник не работает в выбранном магазине'
            })
        
        if sale_debt:
            if deposit and deposit >= total_amount:
                raise serializers.ValidationError({
                    'Депозит не может превышать сумму долга'
                })

        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        sale_items = validated_data.pop('sale_items', None)
        sale_debt = validated_data.pop('sale_debt', None)
        sale_payments = validated_data.pop('sale_payments', None)
        total_amount = validated_data.pop('total_amount', None)
        on_credit = validated_data.get('on_credit')
        store_written = validated_data.pop('store', None)
        sold_by = validated_data.pop('sold_by', None)

        user = self.context['request'].user
        store = user.store
        if user.is_superuser and sold_by and store_written:
            
            new_sale = Sale.objects.create(
                store=store_written,
                sold_by=sold_by,
                **validated_data
            )
        else:
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
        
        new_sale.total_amount = total_amount or new_sale.get_total_amount()

        if on_credit:
            Debt.objects.create(sale=new_sale, store=new_sale.store, total_amount=new_sale.total_amount,**sale_debt)
            new_sale.is_paid = False

        if sale_payments is not None:
            payments_lst = [SalePayment(sale=new_sale, **payment) 
            for payment in sale_payments
            ]
            SalePayment.objects.bulk_create(payments_lst)
        
        new_sale.save()
        
        process_sale(new_sale)

        return new_sale

    def update(self, instance, validated_data):
        validated_data.pop('on_credit', None)
        validated_data.pop('is_paid', None)
        validated_data.pop('sale_items', None)
        validated_data.pop('sale_debt', None)
        validated_data.pop('sale_payments', None)

        for field,value in validated_data.items():
            if value is not None:
                setattr(instance, field, value)

        instance.save()

        return instance

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if not repr['on_credit']:
            repr.pop('is_paid')
        return repr
        



