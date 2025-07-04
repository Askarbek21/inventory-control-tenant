from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from config.permissions import IsAdministrator
from config.pagination import CustomPageNumberPagination
from apps.sales.models import SaleItem
from .serializers import *
from .filters import IncomeFilter


class IncomeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    pagination_class = CustomPageNumberPagination
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    
    def get_queryset(self):
        base_qs = Income.objects.select_related('store', 'sale')

        base_qs = base_qs.prefetch_related(
            Prefetch(
                'sale__sale_items',
                queryset=SaleItem.objects.select_related('stock__product')
            )
        )

        if self.request.user.is_superuser:
            return base_qs

        return base_qs.filter(store=self.request.user.store)
        
