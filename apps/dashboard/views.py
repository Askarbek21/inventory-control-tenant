from django.db.models import Sum
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemsDashboardSerializer
from ..items.models import Product, Stock


# Create your views here.

class ItemsDashboardAPIView(APIView):
    serializer_class = ItemsDashboardSerializer

    def get(self, request):
        stock = Stock.objects.select_related(
            "product",
            "store",
            "supplier",
        ).only(
            'id', 'product',
            'quantity', 'quantity_for_history',
            'store', 'supplier', 'date_of_arrived'
        )
        if request.user.is_superuser:
            stock = stock.all()
            total_product = stock.count()
            info_products = (
                stock.values('product__product_name', 'store__name').annotate(total_quantity=Sum('quantity'))
            )
        elif request.user.role == 'Администратор' or request.user.role == 'Продавец':
            stock = stock.filter(store=request.user.store)

            total_product = stock.count()
            info_products = (
                stock.values('product__product_name', 'store__name').annotate(total_quantity=Sum('quantity'))
            )
        
        return Response({
            "total_product": total_product,
            "info_products": info_products,
        })
