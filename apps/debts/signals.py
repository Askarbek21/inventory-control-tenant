from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.incomes.models import Income
from .models import DebtPayment


@receiver(post_save, sender=DebtPayment)
def increment_store_budget(sender, instance, created, **kwargs):
    store = instance.debt.store
    if created:
        store.budget += instance.amount
        store.save(update_fields=['budget'])

        Income.objects.create(
        store=store, source='Погашение долга', 
        description={
            "Client": instance.debt.client.name,
            "Amount": str(instance.amount),
            "Payment Method": instance.payment_method,
            "Timestamp": str(instance.paid_at),
        }
        )


