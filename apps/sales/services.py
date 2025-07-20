from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
                sale=sale,
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
                            "Amount": str(payment.amount)
                        }
                        for payment in sale.sale_payments.all()
                    ]
                }
            )
        return

    # Юр. лицо
    old_balance = client.balance or 0
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
            sale=sale,
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
        amount_deducted=sale.total_amount,
        worker=sale.sold_by
    )

    client.balance = new_balance
    client.save(update_fields=['balance'])

    if credit_amount > 0:
        Debt.objects.create(
            sale=sale,
            store=store,
            client=client,
            total_amount=credit_amount,
            from_client_balance=True,
        )
        sale.on_credit = True
        sale.is_paid = False
        sale.save(update_fields=['on_credit', 'is_paid'])


def generate_sale_pdf(sale_data: dict) -> BytesIO:
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Чек")

    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Дата: {sale_data.get('created_at').strftime('%d-%m-%Y %H:%M:%S')}")
    p.drawString(100, 760, f"Кассир: {sale_data.get('worker_read', {}).get('name', 'N/A')}")

    # Items
    p.drawString(100, 740, "Товары:")
    y = 720
    for item in sale_data.get("sale_items", []):
        stock_read = item.get("stock_read", {})
        product_read = stock_read.get("product_read", {})
        product_name = product_read.get("product_name", "N/A")
        quantity = item.get("quantity", 0)
        subtotal = item.get("subtotal", 0.0)
        p.drawString(100, y, f"{product_name} x {quantity} — {subtotal:.2f} сум")
        y -= 20

    # Payment
    for payment in sale_data.get("sale_payment", []):
        amount = payment.get("amount", 0.0)
        method = payment.get("payment_method", "N/A")

    y -= 10
    p.drawString(100, y, f"Оплата: {amount:.2f} сум - {method}")

    total = sale_data.get('total_amount', 0.0)
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, f"Общая сумма: {total:.2f} сум")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer