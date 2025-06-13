from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import *


# @receiver(pre_delete, sender=Product)
# def archive_products_before_delete(sender, instance, **kwargs):
#     data = model_to_dict(instance)
#     if instance.category:
#         data['category'] = instance.category.category_name,
#     DeletedItems.objects.create(
#         model=sender,
#         data=data
#     )


@receiver(post_save, sender=Product)
def update_stock_total_volume(sender, instance, **kwargs):
    stock = Stock.objects.filter(product=instance)
    for st in stock:
        if instance.kub is not None and st.quantity is not None:
            st.total_volume = st.quantity * instance.kub
            st.save()
