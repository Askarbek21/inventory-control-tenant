from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

from .models import LoanPayment

@receiver(post_save, sender=LoanPayment)
def handle_loan_payment(sender, instance, created, **kwargs):
    if not created:
        return
    
    debt = instance.loan

    total_paid = debt.loan_payments.aggregate(total=Sum('amount'))['total'] or 0
    if total_paid >= debt.total_amount and not debt.is_paid:
        debt.is_paid = True
        debt.save(update_fields=['is_paid'])