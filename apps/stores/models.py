from django.db import models
from django.conf import settings


class Store(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=13, blank=True, unique=True)
    parent_store = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='children')
    budget = models.DecimalField(max_digits=20, decimal_places=2, default=0)    
    created_at = models.DateTimeField(auto_now_add=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = 'stores'
        ordering = ['name']
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name
