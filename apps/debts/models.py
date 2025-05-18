from django.db import models

from apps.sales.models import Sale 
from apps.clients.models import Client


class Debt(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='sale_debt')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_debts')
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debts'
        ordering = ['-created_at']
        verbose_name_plural = 'Debts'
    
    def __str__(self):
        return f'{self.client.name} | {self.client.phone_number} - {self.total_amount} | {self.due_date}'


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debt_payments'
        ordering = ['-paid_at']
        verbose_name_plural = 'Debt Payments'
    
    def __str__(self):
        return f'{self.debt.customer_name} заплатил {self.amount} в {self.paid_at} '

