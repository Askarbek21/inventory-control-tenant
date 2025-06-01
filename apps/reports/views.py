from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Count
from django.db.models.functions import Cast, TruncDate, Coalesce
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from apps.sales.models import Sale, SaleItem, Stock
from apps.debts.models import Debt
from apps.items.models import Product
from .serializers import *


class SalesSummaryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        period = request.query_params.get('period', 'day')
        today = now()

        if period == 'week':
            start = today - timedelta(days=7)
        elif period == 'month':
            start = today - timedelta(days=30)
        else:
            start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        sales = Sale.objects.filter(sold_date__gte=start, on_credit=False)
        total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_sales = sales.count()

        trend = sales.annotate(day=TruncDate('sold_date')).values('day').annotate(
            total=Sum('total_amount')
        ).order_by('day')

        return Response({
            "total_sales": total_sales, 
            "total_revenue": total_revenue,
            "trend": list(trend),
        })


class TopProductsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        period = request.query_params.get('period', 'month')
        limit = int(request.query_params.get('limit', 5))
        start = now() - timedelta(days=30 if period == 'month' else 7)

        items = SaleItem.objects.filter(sale__sold_date__gte=start).values(
            product_name=F('stock__product__product_name')
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_revenue')[:limit]

        return Response(ProductSalesSerializer(items, many=True).data)


class UnsoldProductsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        cutoff = now() - timedelta(days=days)

        sold_product_ids = SaleItem.objects.filter(
            sale__sold_date__gte=cutoff
        ).values_list('stock__product_id', flat=True)

        unsold_products = Product.objects.exclude(id__in=sold_product_ids)

        data = [{"product_name": p.product_name} for p in unsold_products]

        return Response(data)


class StockByCategoryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        stocks = Stock.objects.values(
            category=F('product__category__category_name')
        ).annotate(
            total_stock=Sum('quantity')
        )

        return Response(StockCategorySerializer(stocks, many=True).data)


class ProductIntakeView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        period = request.query_params.get('period', 'month')

        if period == 'day':
            days = 1
        elif period == 'week':
            days = 7
        else:
            days = 30

        start_date = now() - timedelta(days=days)

        stocks = Stock.objects.filter(date_of_arrived__gte=start_date)

        stocks = stocks.annotate(
            total_value=ExpressionWrapper(
                F('quantity') * F('purchase_price_in_uz'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )

        total_positions = stocks.count()
        total_sum = stocks.aggregate(total=Sum('total_value'))['total'] or 0

        daily_data = (
            stocks.annotate(day=TruncDate('date_of_arrived'))
            .values('day')
            .annotate(
                total_price=Sum('total_value'),
                total_quantity=Sum('quantity')
            )
            .order_by('day')
        )

        return Response({
            'total_positions': total_positions,
            'total_sum': total_sum,
            'data': daily_data
        })


class ProductProfitabilityView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):

        items = SaleItem.objects.exclude(sale__on_credit=True).select_related('stock__product').values(
            product_name=F('stock__product__product_name')
        ).annotate(
            revenue=Sum('subtotal'),
            cost=Sum(ExpressionWrapper(F('stock__purchase_price_in_uz') * F('quantity'), output_field=DecimalField(max_digits=20, decimal_places=2))),
        ).annotate(
            profit=F('revenue') - F('cost'),
            margin=ExpressionWrapper(Cast(F('profit'), DecimalField(max_digits=25, decimal_places=2)) *100 / Cast(F('revenue'), DecimalField(max_digits=20, decimal_places=2)), output_field=DecimalField(max_digits=20, decimal_places=2))
        )

        sort = request.query_params.get('sort', 'profit')
        if sort == 'margin':
            items = sorted(items, key=lambda x: x['margin'], reverse=True)
        else:
            items = sorted(items, key=lambda x: x['profit'], reverse=True)

        return Response(ProductProfitabilitySerializer(items, many=True).data)


class ClientDebtView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        debts = Debt.objects.exclude(is_paid=True).annotate(
            client_name=F('client__name'),
            total_debt=F('total_amount'),
            total_paid=Coalesce(
                Sum('payments__amount'),
                0,
                output_field=DecimalField(max_digits=20, decimal_places=2)
            ),
            remaining_debt=ExpressionWrapper(
                F('total_amount') - F('total_paid') - F('deposit'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ).order_by('-remaining_debt')
        
        debts_data = debts.values(
            'client_name',
            'total_debt',
            'total_paid',
            'remaining_debt',
            'deposit',
        )

        return Response(ClientDebtSerializer(debts_data, many=True).data)


class TopSellersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'month')
        today = now()

        if period == 'day':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = today - timedelta(days=7)
        else:
            start_date = today - timedelta(days=30)

        sellers = Sale.objects.filter(
            sold_date__gte=start_date,
            on_credit=False
        ).values(
            store_name = F('store__name'),
            seller_name=F('sold_by__name'),
            seller_phone=F('sold_by__phone_number')
        ).annotate(
            total_revenue=Sum('total_amount'),
            total_sales=Count('id')
        ).order_by('-total_revenue')

        return Response(sellers)