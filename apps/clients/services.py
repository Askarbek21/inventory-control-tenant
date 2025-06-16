from django.db.models import Sum 
from decimal import Decimal

from apps.debts.models import Debt, DebtPayment
from .models import BalanceHistory


def log_client_balance(client, old_balance, new_balance, request):
    BalanceHistory.objects.create(
        type='Пополнение',
        client=client,
        previous_balance=old_balance,
        new_balance=new_balance,
        worker=request.user
    )


def pay_debts_from_balance(client, worker=None):
    if client.type != 'Юр.лицо' or client.balance >= 0:
        return

    available_amount = abs(client.balance)
    used_amount = Decimal('0.00')

    debts = Debt.objects.filter(
        client=client,
        is_paid=False,
        from_client_balance=True
    ).order_by('created_at')

    for debt in debts:
        total_paid = debt.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = debt.total_amount - total_paid

        if available_amount - used_amount >= remaining:
            DebtPayment.objects.create(
                debt=debt,
                amount=remaining,
                payment_method='Перечисление',
                worker=worker
            )
            used_amount += remaining
        else:
            partial = available_amount - used_amount
            if partial <= 0:
                break
            DebtPayment.objects.create(
                debt=debt,
                amount=partial,
                payment_method='Перечисление',
                worker=worker
            )
            used_amount += partial
            break

    if used_amount > 0:
        client.balance += used_amount 
        client.save(update_fields=['balance'])