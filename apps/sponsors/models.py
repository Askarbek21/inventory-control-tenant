from django.db import models


class Sponsor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    phone_number = models.CharField(max_length=13, unique=True)

    class Meta:
        db_table = 'sponsors'
        verbose_name_plural = 'Sponsors'
        ordering = ['name']
    
    def __str__(self):
        return self.name