from django.db import models

from apps.stores.models import Store
from apps.staff.models import CustomUser


class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = {
        'Наличные': 'Наличные',
        'Карта': 'Карта',
        'Click': 'Click',
        'Сложная оплата': 'Сложная оплата',
    }
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sales')
    sold_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=8, choices=PAYMENT_METHOD_CHOICES, default='Наличные')
    on_credit = models.BooleanField(default=False)
    sold_date = models.DateTimeField(auto_now_add=True)
    ## нужен товар
    