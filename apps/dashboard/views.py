from django.db.models import Sum
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
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
        ).filter(store__owner=request.user.id)

        total_product = stock.count()
        info_products = (
            stock.values('product__product_name', 'store__name').annotate(total_quantity=Sum('quantity'))
        )
        total_product_name = stock.values('product').aggregate()
        print(total_product_name)
        return Response({
            "total_product": total_product,
            "info_products": info_products,
        })
