from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import *


@receiver(pre_delete, sender=Product)
def archive_products_before_delete(sender, instance, **kwargs):
    data = model_to_dict(instance)
    if instance.category:
        data['category'] = instance.category.category_name,
    DeletedItems.objects.create(
        model=sender,
        data=data
    )
