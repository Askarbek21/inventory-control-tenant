from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} -- {self.phone_number}'

    class Meta:
        verbose_name_plural = "Suppliers"
        db_table = 'suppliers'
