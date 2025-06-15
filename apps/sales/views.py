from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from config.permissions import SalePermission
from .serializers import *
from .filters import SaleFilter
from config.pagination import CustomPageNumberPagination

class SaleViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, SalePermission]
    serializer_class = SaleSerializer
    filterset_class = SaleFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_context(self):
        context = {'request': self.request}
        return context
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Sale.objects.prefetch_related('sale_items', 'sale_payments').select_related('store', 'sold_by')
        return Sale.objects.filter(store=self.request.user.store).prefetch_related('sale_items', 'sale_payments').select_related('store', 'sold_by')

