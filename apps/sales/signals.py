from decimal import Decimal, ROUND_HALF_UP
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction

from apps.items.models import MeasurementProduct
from .models import Sale


@receiver(post_save, sender=Sale)
def deduct_quantity_from_stock(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: deduct_stock(instance))

def deduct_stock(instance):
    for item in instance.sale_items.all():
        stock = item.stock
        product = stock.product
        quantity_decimal = Decimal(stock.quantity)

        if item.selling_method == 'Штук':
            quantity_decimal -= Decimal(item.quantity)
            
        else:
            product_measurement = MeasurementProduct.objects.filter(product=product, for_sale=True).first()
            if product_measurement:
                meters_per_piece = product_measurement.number
                required_piece = Decimal(item.quantity) / Decimal(meters_per_piece)
                quantity_decimal -= required_piece

        stock.quantity = quantity_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        stock.save(update_fields=['quantity'])


@receiver(pre_delete, sender=Sale)
def deduct_budget(sender, instance, **kwargs):
    store = instance.store
    with transaction.atomic():
        store.budget -= instance.total_amount
        store.save(update_fields=['budget'])
        






