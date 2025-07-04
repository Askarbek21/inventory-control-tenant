from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import *


@receiver(pre_delete, sender=Expense)
def after_delete_change_balance(sender, instance, **kwargs):
    instance.store.budget += instance.amount
    instance.store.save()


@receiver(pre_delete, sender=CashInFlow)
def change_balance_after_adding_money(sender, instance, **kwargs):
    instance.store.budget -= instance.amount
    instance.store.save()
