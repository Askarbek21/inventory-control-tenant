from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Count
from django.db.models.functions import Cast, TruncDate, Coalesce, TruncMonth
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.permissions import IsAdministrator
from apps.sales.models import Sale, SaleItem, Stock
from apps.debts.models import Debt
from apps.items.models import Product
from apps.expenses.models import Expense
from .serializers import *
from .utils import get_date_range_with_period


class SalesSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    
    def get(self, request):
        date_from, date_to = get_date_range_with_period(request)
        store = request.query_params.get('store')
        user = request.user

        sales = Sale.objects.filter(sold_date__range=(date_from, date_to), is_paid=True)
        if store and user.is_superuser:
            sales = sales.filter(store=store)
        if not user.is_superuser:
            sales = sales.filter(store=user.store)
        total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_sales = sales.count()

        trend = sales.annotate(month=TruncMonth('sold_date')).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        return Response({
            "total_sales": total_sales, 
            "total_revenue": total_revenue,
            "trend": list(trend),
        })


class TopProductsView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    def get(self, request):
        date_from, date_to = get_date_range_with_period(request)
        store = request.query_params.get('store')
        user = request.user
        limit = int(request.query_params.get('limit', 5))

        items = SaleItem.objects.filter(sale__sold_date__range=(date_from, date_to))
        if store and user.is_superuser:
            items = items.filter(sale__store=store)
        if not user.is_superuser:
            items = items.filter(sale__store=user.store)
        items = items.values(
            product_name=F('stock__product__product_name')
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_revenue')[:limit]

        return Response(ProductSalesSerializer(items, many=True).data)


class UnsoldProductsView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        cutoff = now() - timedelta(days=days)
        store = request.query_params.get('store')
        user = request.user

        sold_product_ids = SaleItem.objects.filter(
            sale__sold_date__gte=cutoff
        )
        if store and user.is_superuser:
            sold_product_ids = sold_product_ids.filter(sale__store=store)
        if not user.is_superuser:
            sold_product_ids = sold_product_ids.filter(sale__store=user.store)
        sold_product_ids = sold_product_ids.values_list('stock__product_id', flat=True)

        unsold_products = Product.objects.exclude(id__in=sold_product_ids)

        data = [{"product_name": p.product_name} for p in unsold_products]

        return Response(data)


class StockByCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    def get(self, request):
        store = request.query_params.get('store')
        user = request.user
        stocks = Stock.objects.all()
        if store and user.is_superuser:
            stocks = stocks.filter(store=store)
        if not user.is_superuser:
            stocks = stocks.filter(store=user.store)
        stocks = stocks.values(
            category=F('product__category__category_name')
        ).annotate(
            total_stock=Sum('quantity')
        )

        return Response(StockCategorySerializer(stocks, many=True).data)


class ProductIntakeView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        date_from, date_to = get_date_range_with_period(request)
        store = request.query_params.get('store')
        user = request.user

        stocks = Stock.objects.filter(date_of_arrived__range=(date_from, date_to))
        if store and user.is_superuser:
            stocks = stocks.filter(store=store)
        if not user.is_superuser:
            stocks = stocks.filter(store=user.store)
        stocks = stocks.annotate(
            total_value=ExpressionWrapper(
                F('quantity') * F('selling_price'),
                output_field=DecimalField(max_digits=50, decimal_places=2)
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
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        store = request.query_params.get('store')
        user = request.user

        items = SaleItem.objects.filter(sale__is_paid=True).select_related('stock__product')
        if store and user.is_superuser:
            items = items.filter(sale__store=store)
        if not user.is_superuser:
            items = items.filter(sale__store=user.store)
        items = items.values(
            product_name=F('stock__product__product_name')
        ).annotate(
            revenue=Sum('subtotal'),
            cost=Sum(ExpressionWrapper(F('stock__purchase_price_in_uz') * F('quantity'), output_field=DecimalField(max_digits=40, decimal_places=2))),
        ).annotate(
            profit=F('revenue') - F('cost'),
            margin=ExpressionWrapper(Cast(F('profit'), DecimalField(max_digits=50, decimal_places=2)) *100 / Cast(F('revenue'), DecimalField(max_digits=50, decimal_places=2)), output_field=DecimalField(max_digits=50, decimal_places=2))
        )

        sort = request.query_params.get('sort', 'profit')
        if sort == 'margin':
            items = sorted(items, key=lambda x: x['margin'], reverse=True)
        else:
            items = sorted(items, key=lambda x: x['profit'], reverse=True)

        return Response(ProductProfitabilitySerializer(items, many=True).data)


class ClientDebtView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        store = request.query_params.get('store')
        user = request.user
        debts = Debt.objects.exclude(is_paid=True)
        
        if store and user.is_superuser:
            debts = debts.filter(store=store)
        if not user.is_superuser:
            debts = debts.filter(store=user.store)
            
        debts = debts.values(
            client_name=F('client__name')
        ).annotate(
            total_debt=Coalesce(
                Sum('total_amount'),
                0,
                output_field=DecimalField(max_digits=50, decimal_places=2)
            ),
            total_paid=Coalesce(
                Sum('payments__amount'),
                0,
                output_field=DecimalField(max_digits=50, decimal_places=2)
            ),
            deposit=Coalesce(
                Sum('deposit'),
                0,
                output_field=DecimalField(max_digits=50, decimal_places=2)
            ),
        ).annotate(
            remaining_debt=ExpressionWrapper(
                F('total_debt') - F('total_paid') - F('deposit'),
                output_field=DecimalField(max_digits=50, decimal_places=2)
            )
        ).order_by('-remaining_debt')

        return Response(ClientDebtSerializer(debts, many=True).data)


class TopSellersView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        store = request.query_params.get('store')
        date_from, date_to = get_date_range_with_period(request)
        user = request.user

        sellers = Sale.objects.filter(
            sold_date__range=(date_from, date_to),
            is_paid=True
        )
        if store and user.is_superuser:
            sellers = sellers.filter(store=store)
        if not user.is_superuser:
            sellers = sellers.filter(store=user.store)
        sellers = sellers.values(
            store_name = F('store__name'),
            seller_name=F('sold_by__name'),
            seller_phone=F('sold_by__phone_number')
        ).annotate(
            total_revenue=Sum('total_amount'),
            total_sales=Count('id')
        ).order_by('-total_revenue')

        return Response(list(sellers))


class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        store = request.query_params.get('store')
        date_from, date_to = get_date_range_with_period(request)
        user = request.user
        expenses = Expense.objects.filter(date__range=(date_from, date_to))
        if store and user.is_superuser:
            expenses = expenses.filter(store=store)
        if not user.is_superuser:
            expenses = expenses.filter(store=user.store)
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

        grouped = (
            expenses
            .values('expense_name__name')
            .annotate(total_amount=Sum('amount'))
            .order_by('expense_name__name')
        )

        return Response({
            "total_expense": total_expense,
            "expenses": list(grouped)
        })



class SalesmanSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        date_from, date_to = get_date_range_with_period(request)

        sales = Sale.objects.filter(sold_date__range=(date_from, date_to), sold_by=request.user, is_paid=True)
        total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_sales = sales.count()

        return Response({
            "total_sales": total_sales, 
            "total_revenue": total_revenue,
        })


class SalesmanDebtView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        date_from, date_to = get_date_range_with_period(request)

        debts = Debt.objects.filter(sale__sold_by=user, is_paid=False, created_at__range=(date_from, date_to))
        total_debt = debts.aggregate(total=Sum('total_amount'))['total'] or 0
        count = debts.count()
    
        return Response({
            "total_count": count, 
            "total_debt": total_debt,
        })
    

class SalesProfitView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    def get(self,request):
        date_from, date_to = get_date_range_with_period(request)
        store = request.query_params.get('store')
        user = request.user

        sales = Sale.objects.filter(sold_date__range=(date_from, date_to), is_paid=True)

        if store and user.is_superuser:
            sales = sales.filter(store=store)
        if not user.is_superuser:
            sales = sales.filter(store=user.store)
        
        total_sales = sales.count()
        total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_pure_revenue = sales.aggregate(total=Sum('total_pure_revenue'))['total'] or 0
        
        response_data = {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_pure_revenue': total_pure_revenue,
        }
        
        return Response(response_data)
