from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Sale


@receiver(post_save, sender=Sale)
def deduct_quantity_from_stock(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: deduct_stock(instance))

def deduct_stock(instance):
    for item in instance.sale_items.all():
        stock = item.stock
        stock.quantity -= item.quantity
        stock.save(update_fields=['quantity'])


