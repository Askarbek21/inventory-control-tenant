from django.db.models.signals import pre_delete, post_save,post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import *
from django.core.cache import cache

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
    print(cache.keys("*"))
    print("signal")
    CACHE_PREFIX = "views.decorators.cache"
    #cache.delete_pattern(f"{CACHE_PREFIX}.cache_page.product_list*")
    #cache.delete_pattern(f"{CACHE_PREFIX}.cache_header.product_list*")
    cache.delete_pattern("product_list_*")
    print("Good")
    print(cache.keys("*"))


@receiver(post_delete, sender=Product)
def clear_cache_on_delete(sender, instance, **kwargs):
    print(cache.keys("*"))
    print("signal")
    CACHE_PREFIX = "views.decorators.cache"
    #cache.delete_pattern(f"{CACHE_PREFIX}.cache_page.product_list*")
    #cache.delete_pattern(f"{CACHE_PREFIX}.cache_header.product_list*")
    cache.delete_pattern("product_list_*")
    print("Good")
    print(cache.keys("*"))
