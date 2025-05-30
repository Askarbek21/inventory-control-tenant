from .models import BalanceHistory


def log_client_balance(client, old_balance, new_balance, request):
    BalanceHistory.objects.create(
        type='Пополнение',
        client=client,
        previous_balance=old_balance,
        new_balance=new_balance,
        worker=request.user
    )