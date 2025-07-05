from django.db import transaction
from .models import Loan, LoanPayment


def apply_existing_overpayment(loan: Loan):
    previous = (
        Loan.objects
        .filter(
            sponsor=loan.sponsor,
            currency=loan.currency,
            overpayment_unused__gt=0
        )
        .order_by('-created_at')
        .first()
    )
    if not previous:
        return 
    apply_amount = min(loan.remaining_balance, previous.overpayment_unused)
    if apply_amount > 0:
        LoanPayment.objects.create(
            loan=loan,
            amount=apply_amount,
            payment_method='Перечисление',
            notes=f'Автоматическое перечисление от взаимы #{previous.id}'
        )
        loan.remaining_balance -= apply_amount
        if loan.remaining_balance <= 0:
            loan.remaining_balance = 0
            loan.is_paid = True
        loan.save(update_fields=['remaining_balance', 'is_paid'])
        previous.overpayment_unused -= apply_amount
        previous.save(update_fields=['overpayment_unused'])


def apply_loan_payment(loan: Loan, amount, payment_method, notes=''):

    with transaction.atomic():
        to_apply = amount
        initial_remaining_balance = loan.remaining_balance
        new_payment = LoanPayment.objects.create(
            loan=loan,
            amount=to_apply,
            payment_method=payment_method,
            notes=notes
        )

        loan.remaining_balance -= to_apply
        if loan.remaining_balance <= 0:
            loan.remaining_balance = 0
            loan.is_paid = True
            overpaid = amount - initial_remaining_balance
            if overpaid > 0:
                loan.overpayment_unused += overpaid
        loan.save()
        return new_payment