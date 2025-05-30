from apps.incomes.models import Income
from apps.clients.models import BalanceHistory
from apps.debts.models import Debt
from .models import Sale


def process_sale(sale: Sale):
    client = sale.client
    store = sale.store

    if client is None:
        if not sale.on_credit:
            store.budget += sale.total_amount
            store.save(update_fields=['budget'])

            Income.objects.create(
                source='Продажа',
                store=store,
                worker=sale.sold_by,
                description={
                    "Amount": str(sale.total_amount),
                    "Sold Date": str(sale.sold_date),
                    "Items": [
                        {
                            "Product": item.stock.product.product_name,
                            "Quantity": str(item.quantity),
                            "Selling Method": item.selling_method,
                            "Subtotal": str(item.subtotal)
                        }
                        for item in sale.sale_items.select_related('stock__product')
                    ],
                    "Payments": [
                        {
                            "Method": payment.payment_method,
                            "Amount": payment.amount
                        }
                        for payment in sale.sale_payments.all()
                    ]
                }
            )
        return

    # Юр. лицо
    old_balance = client.balance
    paid_amount = min(max(old_balance, 0), sale.total_amount)
    credit_amount = sale.total_amount - paid_amount
    new_balance = old_balance - sale.total_amount

    if paid_amount > 0:
        store.budget += paid_amount
        store.save(update_fields=['budget'])

        Income.objects.create(
            source='Продажа',
            store=store,
            worker=sale.sold_by,
            description={
                "Amount": str(paid_amount),
                "Sold Date": str(sale.sold_date),
                "Items": [
                        {
                            "Product": item.stock.product.product_name,
                            "Quantity": str(item.quantity),
                            "Selling Method": item.selling_method,
                            "Subtotal": str(item.subtotal)
                        }
                        for item in sale.sale_items.select_related('stock__product')
                    ],
                "Payments": [
                    {
                        "Method": "Перечисление",
                        "Amount": str(paid_amount)
                    }
                ]
            }
        )

    BalanceHistory.objects.create(
        type='Расход',
        client=client,
        sale=sale,
        previous_balance=old_balance,
        new_balance=new_balance,
        amount_deducted=paid_amount,
        worker=sale.sold_by
    )

    client.balance = new_balance
    client.save(update_fields=['balance'])

    if credit_amount > 0:
        Debt.objects.create(
            sale=sale,
            store=store,
            client=client,
            total_amount=credit_amount
        )
        sale.on_credit = True
        sale.save(update_fields=['on_credit'])