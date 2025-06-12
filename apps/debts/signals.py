from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.incomes.models import Income
from .models import DebtPayment, Debt


@receiver(post_save, sender=DebtPayment)
def increment_store_budget(sender, instance, created, **kwargs):
    store = instance.debt.store
    if created:
        store.budget += instance.amount
        store.save(update_fields=['budget'])

        Income.objects.create(
        store=store, 
        source='Погашение долга',
        worker=instance.worker,
        description={
            "Client": instance.debt.client.name,
            "Amount": str(instance.amount),
            "Payment Method": instance.payment_method,
            "Timestamp": str(instance.paid_at),
        }
        )


@receiver(post_save, sender=Debt)
def update_related_sale(sender, instance, created, **kwargs):
    sale = instance.sale
    client = instance.client
    if created:
        return 
    if instance.is_paid:
        sale.is_paid = True
        sale.save(update_fields=['is_paid'])
        if instance.from_client_balance:
            client.balance += instance.total_amount
            client.save(update_fields=['balance'])
        return 

