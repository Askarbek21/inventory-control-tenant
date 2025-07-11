from django.db import models

from apps.stores.models import Store
from config import constants


# Create your models here.
class ExpenseName(models.Model):
    name = models.CharField(max_length=254)

    class Meta:
        db_table = 'expenses_name'
        ordering = ['name']

    def __str__(self):
        return self.name


class CashInFlowName(models.Model):
    name = models.CharField(max_length=254)

    class Meta:
        db_table = 'cash_in_flow_name'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    expense_name = models.ForeignKey(ExpenseName, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    comment = models.CharField(max_length=254, null=True, blank=True)
    payment_type = models.CharField(max_length=254, null=True, blank=True, choices=constants.PAYMENT_METHOD_CHOICES)
    user = models.CharField(max_length=254, null=True, blank=True)
    history = models.JSONField(default=dict)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-date']


class CashInFlow(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    cash_inflow_name = models.ForeignKey(CashInFlowName, on_delete=models.SET_NULL,
                                         null=True)
    comment = models.CharField(max_length=254, null=True, blank=True)
    user = models.CharField(max_length=254, null=True, blank=True)
    history = models.JSONField(default=dict, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cash_inflows'
