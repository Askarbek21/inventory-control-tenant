from django.db import models


class SiteConfig(models.Model):
    auto_deduct_debt = models.BooleanField(default=False)
    debt_deduction_delay_days = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        
    def __str__(self):
        return f'Site Settings'
    
    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(id=1)[0]
    
