from django.db import transaction
from .models import Loan, LoanPayment


def apply_existing_overpayment(loan: Loan):
    overpayment_loans = (
        Loan.objects
        .filter(
            sponsor=loan.sponsor,
            currency=loan.currency,
            overpayment_unused__gt=0
        )
        .order_by('created_at')
    )

    unpaid_loans = (
        Loan.objects
        .filter(
            sponsor=loan.sponsor,
            currency=loan.currency,
            is_paid=False
        )
        .exclude(id__in=overpayment_loans.values_list('id', flat=True))
        .order_by('created_at')
    )

    for overpaying_loan in overpayment_loans:
        for unpaid_loan in unpaid_loans:
            if overpaying_loan.overpayment_unused <= 0:
                break

            apply_amount = min(unpaid_loan.remaining_balance, overpaying_loan.overpayment_unused)

            if apply_amount > 0:
                LoanPayment.objects.create(
                    loan=unpaid_loan,
                    amount=apply_amount,
                    payment_method='Перечисление',
                    notes=f'Автоматическое перечисление от займа #{overpaying_loan.id}'
                )

                unpaid_loan.remaining_balance -= apply_amount
                if unpaid_loan.remaining_balance <= 0:
                    unpaid_loan.remaining_balance = 0
                    unpaid_loan.is_paid = True
                unpaid_loan.save(update_fields=['remaining_balance', 'is_paid'])

                overpaying_loan.overpayment_unused -= apply_amount
                overpaying_loan.save(update_fields=['overpayment_unused'])



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
        overpaid = 0
        if loan.remaining_balance <= 0:
            overpaid = abs(loan.remaining_balance)
            loan.remaining_balance = 0
            loan.is_paid = True
            overpaid = amount - initial_remaining_balance
            if overpaid > 0:
                loan.overpayment_unused += overpaid
        loan.save()


        if overpaid > 0:
            apply_existing_overpayment(loan)
        return new_payment
