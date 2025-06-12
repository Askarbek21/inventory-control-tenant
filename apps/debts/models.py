from django.db import models

from config.constants import PAYMENT_METHOD_CHOICES
from apps.sales.models import Sale 
from apps.clients.models import Client
from apps.stores.models import Store
from apps.staff.models import CustomUser


class Debt(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='sale_debt')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_debts')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_debts')
    due_date = models.DateField(null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0.0)
    is_paid = models.BooleanField(default=False)
    from_client_balance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debts'
        ordering = ['-created_at']
        verbose_name_plural = 'Debts'
    
    def __str__(self):
        return f'{self.client.name} | {self.client.phone_number} - {self.total_amount} | {self.due_date}'


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHOD_CHOICES)
    worker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='registered_payments')
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debt_payments'
        ordering = ['-paid_at']
        verbose_name_plural = 'Debt Payments'
    
    def __str__(self):
        return f'{self.debt.client.name} заплатил {self.amount} в {self.paid_at} '

