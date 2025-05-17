from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from apps.admin.models import SiteConfig
from config.celery import app
from .models import Debt


@shared_task
def deduct_due_debts():
    settings = SiteConfig.get_solo()

    if not settings.auto_deduct_debt:
        return

    delay_days = settings.debt_deduction_delay_days
    target_date = timezone.now().date() - timedelta(days=delay_days)

    due_debts = Debt.objects.select_related('client').filter(
        due_date__lte=target_date,
        is_paid=False
    )

    for debt in due_debts:
        client = debt.client
        if client.balance >= debt.total_amount:
            client.balance -= debt.total_amount
            client.save(update_fields=['balance'])

            debt.is_paid = True
            debt.save(update_fields=['is_paid'])
        else:
            pass


