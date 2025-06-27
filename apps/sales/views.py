from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

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


class SaleItemViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SaleItemSerializer

    def get_queryset(self):
        return SaleItem.objects.filter(sale=self.kwargs['sale_pk']).select_related('stock', 'sale')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['sale_pk'] = self.kwargs['sale_pk']
        return context
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sale.sale_items.count() <= 1:
            return Response(
                {"detail": "Нельзя удалить последний товар из продажи."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SalePaymentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SalePaymentSerializer

    def get_queryset(self):
        return SalePayment.objects.filter(sale=self.kwargs['sale_pk']).select_related('sale')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['sale_pk'] = self.kwargs['sale_pk']
        return context
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sale.sale_payments.count() <= 1:
            return Response(
                {"detail": "Нельзя удалить последнюю оплату из продажи."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)