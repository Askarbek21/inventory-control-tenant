from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.items.models import Product, Stock
from apps.stores.models import Store


class Transfer(models.Model):
    from_stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='from_stock')
    to_stock = models.ForeignKey(Store, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True, related_name='stock')
    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.0)])
    date_of_transfer = models.DateTimeField(default=timezone.now)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.from_stock.store} - {self.to_stock}'

    def clean(self):
        if (self.amount < 0 or self.amount > self.from_stock.quantity) or self.from_stock.store.id == self.to_stock.id:
            raise ValidationError('Amount must be greater than 0 and less than or equal to the quantity in stock.')

    class Meta:
        verbose_name = 'Transfer'
        ordering = ['-date_of_transfer']
        db_table = 'transfer'
