from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm 

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
    # Create a narrow page (like supermarket receipts)
    width = 80 * mm  # Typical receipt width
    height = 297 * mm  # A4 height
    pagesize = portrait((width, height))
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=pagesize)
    
    # Set initial position (starting from top)
    x = 5 * mm
    y = height - 10 * mm  # Start 10mm from top
    
    # Header
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, y, "ЧЕК")
    y -= 8 * mm
    
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, y, f"Дата: {sale_data.get('sold_date', 'N/A')}")
    y -= 5 * mm
    p.drawCentredString(width/2, y, f"Кассир: {sale_data.get('worker_read', {}).get('name', 'N/A')}")
    y -= 8 * mm
    
    # Items header
    p.line(x, y, width - x, y)
    y -= 5 * mm
    p.setFont("Helvetica-Bold", 9)
    p.drawString(x, y, "Товар")
    p.drawString(width - 25 * mm, y, "Кол-во")
    p.drawString(width - 15 * mm, y, "Сумма")
    y -= 5 * mm
    p.line(x, y, width - x, y)
    y -= 3 * mm
    
    # Items list
    p.setFont("Helvetica", 9)
    for item in sale_data.get("sale_items", []):
        stock_read = item.get("stock_read", {})
        product_read = stock_read.get("product_read", {})
        product_name = product_read.get("product_name", "N/A")
        quantity = float(item.get("quantity", 0))
        subtotal = float(item.get("subtotal", 0.0))
        
        # Split long product names into multiple lines
        max_chars = 25
        if len(product_name) > max_chars:
            parts = [product_name[i:i+max_chars] for i in range(0, len(product_name), max_chars)]
            for part in parts:
                p.drawString(x, y, part)
                y -= 4 * mm
        else:
            p.drawString(x, y, product_name)
        
        p.drawString(width - 25 * mm, y, f"{quantity:.2f}")
        p.drawString(width - 15 * mm, y, f"{subtotal:.2f}")
        y -= 6 * mm
    
    # Total line
    p.line(x, y, width - x, y)
    y -= 5 * mm
    total = float(sale_data.get('total_amount', 0.0))
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "ИТОГО:")
    p.drawString(width - 15 * mm, y, f"{total:.2f}")
    y -= 8 * mm
    
    # Payment methods
    p.setFont("Helvetica", 9)
    for payment in sale_data.get("sale_payment", []):
        amount = float(payment.get("amount", 0.0))
        method = payment.get("payment_method", "N/A")
        p.drawString(x, y, f"Оплата ({method}): {amount:.2f}")
        y -= 5 * mm
    
    # Footer
    y -= 10 * mm
    p.setFont("Helvetica", 8)
    p.drawCentredString(width/2, y, "Спасибо за покупку!")
    y -= 4 * mm
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
