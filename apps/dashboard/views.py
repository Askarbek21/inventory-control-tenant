from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from .filters import StockDashboardFilter
from config.pagination import CustomPageNumberPagination
from .serializers import ItemsDashboardSerializer
from ..items.models import Product, Stock


class ItemsDashboardAPIView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StockDashboardFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = Stock.objects.select_related(
            "product", "store", "supplier"
        ).only(
            'id', 'product',
            'quantity', 'quantity_for_history',
            'store', 'supplier', 'date_of_arrived'
        )
        if self.request.user.is_superuser:
            return qs.all()
        elif self.request.user.role in ['Администратор', 'Продавец']:
            return qs.filter(store=self.request.user.store)
        else:
            return qs.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)

        total_product = filtered_queryset.count()

        info_products = filtered_queryset.values(
            'product__product_name', 'store__name'
        ).annotate(total_quantity=Sum('quantity'), total_kub_volume=Sum("total_volume")).order_by(
            'product__product_name')
        total_volume = filtered_queryset.aggregate(Sum('total_volume'))

        page = self.paginate_queryset(info_products)
        if page is not None:
            return self.get_paginated_response({
                "total_product": total_product,
                "info_products": list(page),
                "total_volume": total_volume['total_volume__sum'] or 0

            })

        return Response({
            "total_product": total_product,
            "info_products": list(info_products),
            "total_volume": total_volume['total_volume__sum'] or 0
        })
