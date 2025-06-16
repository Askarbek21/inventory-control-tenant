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
    if client.type != 'Юр.лицо':
        return

    unpaid_debts = Debt.objects.filter(client=client, is_paid=False).order_by('created_at')

    for debt in unpaid_debts:
        total_paid = debt.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = debt.total_amount - total_paid

        if client.balance >= remaining:
            DebtPayment.objects.create(
                debt=debt,
                amount=remaining,
                payment_method='Перечисление',
                worker=worker
            )
            client.balance -= remaining
        else:
            DebtPayment.objects.create(
                debt=debt,
                amount=abs(client.balance),
                payment_method='Перечисление',
                worker=worker
            )
            client.balance = Decimal('0.00')
            break

    client.save(update_fields=['balance'])
