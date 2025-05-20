from django.db.models.signals import post_save
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
        if item.selling_method == 'Штук':
            stock.quantity -= item.quantity
            stock.save(update_fields=['quantity'])
        else:
            product_measurement = MeasurementProduct.objects.get(product=product, for_sale=True)
            product_measurement.number -= item.quantity
            product_measurement.save(update_fields=['number'])


