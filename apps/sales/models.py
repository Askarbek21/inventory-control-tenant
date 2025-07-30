from django.db import models

from apps.stores.models import Store
from apps.staff.models import CustomUser
from apps.items.models import Stock
from apps.clients.models import Client
from config.constants import PAYMENT_METHOD_CHOICES, SELLING_METHOD_CHOICES


class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sales')
    sold_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    total_pure_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    on_credit = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=True)
    sold_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-sold_date']
        verbose_name_plural = 'Sales'
    
    def __str__(self):
        return f'{self.sold_by.name} совершил продажу в {self.sold_date}'
    
    def get_total_amount(self):
        return sum(item.subtotal for item in self.sale_items.all())


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1)
    selling_method = models.CharField(max_length=12, choices=SELLING_METHOD_CHOICES)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        db_table = 'sale_items'
        verbose_name_plural = 'Sale Items'
    
    def __str__(self):
        return f'{self.stock.product.product_name} - {self.quantity}'
    

class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_payments')
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sale_payments'
        verbose_name_plural = 'Sale Payments'
        ordering = ['-paid_at']