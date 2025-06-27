from decimal import Decimal, ROUND_HALF_UP
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.db import transaction

from apps.items.models import MeasurementProduct
from .models import Sale, SaleItem


@receiver(pre_save, sender=SaleItem)
def cache_old_sale_item_state(sender, instance, **kwargs):
    """Сохраняем старые значения quantity и selling_method"""
    if instance.pk:
        try:
            old_instance = SaleItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity
            instance._old_selling_method = old_instance.selling_method
        except SaleItem.DoesNotExist:
            instance._old_quantity = None
            instance._old_selling_method = None
    else:
        instance._old_quantity = None
        instance._old_selling_method = None


@receiver(post_save, sender=SaleItem)
def adjust_stock_after_sale_item_save(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: adjust_stock(instance, instance.quantity, instance.selling_method))
    else:
        old_quantity = getattr(instance, '_old_quantity', None)
        old_method = getattr(instance, '_old_selling_method', None)

        if old_quantity is not None and old_method is not None:
            def update_stock():
                
                adjust_stock(instance, old_quantity, old_method, increase=True)

                adjust_stock(instance, instance.quantity, instance.selling_method, increase=False)

            transaction.on_commit(update_stock)


def adjust_stock(instance, quantity, method, increase=False):
    stock = instance.stock
    product = stock.product
    quantity_decimal = Decimal(quantity)
    stock_qty = Decimal(stock.quantity)

    if method == 'Штук':
        delta = quantity_decimal
    else:
        product_measurement = MeasurementProduct.objects.filter(product=product, for_sale=True).first()
        if not product_measurement:
            return
        meters_per_piece = Decimal(product_measurement.number)
        delta = quantity_decimal / meters_per_piece

    if increase:
        stock_qty += delta
    else:
        stock_qty -= delta

    stock.quantity = stock_qty.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    stock.save(update_fields=['quantity'])


@receiver(pre_delete, sender=Sale)
def deduct_budget(sender, instance, **kwargs):
    store = instance.store
    with transaction.atomic():
        store.budget -= instance.total_amount
        store.save(update_fields=['budget'])
        

@receiver(pre_delete, sender=SaleItem)
def restore_stock_on_saleitem_delete(sender, instance, **kwargs):
    def rollback_stock():
        adjust_stock(instance, instance.quantity, instance.selling_method, increase=True)

    transaction.on_commit(rollback_stock)





