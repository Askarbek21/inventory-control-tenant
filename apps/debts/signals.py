from django.db.models.signals import post_save, pre_delete
from django.db.models import Sum 
from django.dispatch import receiver
from django.db import transaction

from apps.incomes.models import Income
from .models import DebtPayment, Debt


@receiver(post_save, sender=DebtPayment)
def handle_debt_payment(sender, instance, created, **kwargs):
    if not created:
        return

    debt = instance.debt
    client = debt.client
    store = debt.store

    with transaction.atomic():
        store.budget += instance.amount
        store.save(update_fields=['budget'])

        Income.objects.create(
            store=store,
            source='Погашение долга',
            worker=instance.worker,
            description={
                "Client": client.name,
                "Amount": str(instance.amount),
                "Payment Method": instance.payment_method,
                "Timestamp": str(instance.paid_at),
            }
        )

        total_paid = debt.payments.aggregate(total=Sum('amount'))['total'] or 0
        if total_paid >= debt.total_amount - debt.deposit and not debt.is_paid:
            debt.is_paid = True
            debt.save(update_fields=['is_paid'])


@receiver(post_save, sender=Debt)
def update_related_sale(sender, instance, created, **kwargs):
    store = instance.store 
    sale = instance.sale
    client = instance.client

    if created:
        store.budget += instance.deposit
        store.save(update_fields=['budget'])

    if instance.is_paid:
        with transaction.atomic():
            sale.is_paid = True
            sale.save(update_fields=['is_paid'])
            if instance.from_client_balance and client.balance < 0:
                client.balance += instance.total_amount
                client.save(update_fields=['balance'])
            return 


@receiver(pre_delete, sender=DebtPayment)
def deduct_from_budget(sender, instance, **kwargs):
    store = instance.debt.store 
    with transaction.atomic():
        store.budget -= instance.amount
        store.save(update_fields=['budget'])


@receiver(pre_delete, sender=Debt)
def debt_deduct_from_budget(sender, instance, **kwargs):
    store = instance.store 
    with transaction.atomic():
        store.budget -= instance.deposit
        store.save(update_fields=['budget'])