from django.db import models

from config.constants import SOURCE_TYPE_CHOICES
from apps.stores.models import Store
from apps.sales.models import Sale
from apps.debts.models import DebtPayment
from apps.staff.models import CustomUser


class Income(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, null=True)
    debt_payment = models.OneToOneField(DebtPayment, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=15, choices=SOURCE_TYPE_CHOICES)
    description = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'incomes'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.source} - {self.timestamp}'
    

