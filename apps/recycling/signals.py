from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import *

@receiver(post_delete, sender=Recycling)
def after_delete_change_balance(sender, instance, **kwargs):
    if instance.from_to_id:
        instance.from_to.quantity += instance.spent_amount
        instance.from_to.save()

    if instance.to_stock_id:
        try:
            instance.to_stock.delete()
        except Stock.DoesNotExist:
            pass