from django.db import models
from django.utils import timezone

from apps.items.models import Stock, Product


class Recycling(models.Model):
    from_to = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='recycled_from')
    to_stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='recycled_to', null=True, blank=True, )
    to_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_of_recycle = models.DateField(auto_now=True)
    spent_amount = models.FloatField(default=0)
    quantity_of_parts = models.CharField(max_length=50,null=True, blank=True,)

    get_amount = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'recycling'
        ordering = ['-date_of_recycle']

    def __str__(self):
        return f'{self.from_to.product.product_name} - {self.to_product.product_name}'
