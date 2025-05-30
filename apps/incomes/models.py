from django.db import models

from config.constants import SOURCE_TYPE_CHOICES
from apps.stores.models import Store
from apps.staff.models import CustomUser


class Income(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    source = models.CharField(max_length=15, choices=SOURCE_TYPE_CHOICES)
    description = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'incomes'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.source - self.timestamp}'
    

