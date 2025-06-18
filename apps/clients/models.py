from decimal import Decimal
from django.db import models

from apps.staff.models import CustomUser
from apps.stores.models import Store
from config.constants import CLIENT_TYPE_CHOICES, BALANCE_HISTORY_TYPE_CHOICES


class Client(models.Model):
    type = models.CharField(max_length=8, choices=CLIENT_TYPE_CHOICES)
    name = models.CharField(max_length=64, unique=True)
    ceo_name = models.CharField(max_length=64, blank=True, null=True)
    phone_number = models.CharField(max_length=13, unique=True)
    address = models.CharField(max_length=64, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    stores = models.ManyToManyField(Store, related_name='store_clients')

    class Meta:
        db_table = 'clients'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.name
    
    def increment_balance(self, amount):
        self.balance = (self.balance or Decimal('0.00')) + amount
        self.save(update_fields=['balance'])


class BalanceHistory(models.Model):
    type = models.CharField(max_length=10, choices=BALANCE_HISTORY_TYPE_CHOICES)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='balance_history')
    sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2)
    new_balance = models.DecimalField(max_digits=10, decimal_places=2)
    amount_deducted = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'balance_histories'
        ordering = ['-timestamp']
        verbose_name_plural = 'Balance Histories'
    
    def __str__(self):
        return f"{self.client.name}: {self.previous_balance} -> {self.new_balance}"

