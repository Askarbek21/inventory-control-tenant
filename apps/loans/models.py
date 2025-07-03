from django.db import models

from config.constants import CURRENCY_CHOICES, PAYMENT_METHOD_CHOICES
from apps.sponsors.models import Sponsor


class Loan(models.Model):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name='sponsor_loans')
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=6, choices=CURRENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True)
    is_paid = models.BooleanField(default=False)
    remaining_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    overpayment_unused = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    class Meta:
        db_table = 'loans'
        ordering = ['-created_at']
        verbose_name_plural = 'Loans'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.remaining_balance = self.total_amount
        super().save(*args, **kwargs)
    

class LoanPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_payments')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHOD_CHOICES)
    notes = models.TextField(null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_payments'
        ordering = ['-paid_at']
        verbose_name_plural = 'Loan Payments'

