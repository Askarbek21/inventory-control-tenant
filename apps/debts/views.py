from django.db.models import Sum 
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from config.permissions import DebtPermission, DebtPaymentPermission
from config.pagination import CustomPageNumberPagination
from apps.clients.filters import ClientFilter
from .serializers import *
from .filters import DebtFilter, DebtPaymentFilter


class DebtViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DebtPermission]
    pagination_class = CustomPageNumberPagination
    serializer_class = DebtSerializer
    filterset_class = DebtFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Debt.objects.select_related('client', 'store', 'sale')
        return Debt.objects.filter(store=self.request.user.store).select_related('client', 'store', 'sale')


class DebtPaymentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DebtPaymentPermission]
    serializer_class = DebtPaymentSerializer
    filterset_class = DebtPaymentFilter

    def get_queryset(self):
        qs = DebtPayment.objects.filter(debt=self.kwargs['debt_pk']).select_related('worker')
        return qs
    
    def get_serializer_context(self):
        context = {'request': self.request}
        return context


class DebtsGroupedByClientView(generics.ListAPIView):
    serializer_class = ClientDebtSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = ClientFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user 
        store = user.store
        if user.is_superuser:
            return (
            Client.objects
            .filter(client_debts__is_paid=False)
            .annotate(
                total_amount=Sum('client_debts__total_amount'),
                total_deposit=Sum('client_debts__deposit'),
            )
            .order_by('-total_amount')
        )
        return (
            Client.objects
            .filter(client_debts__store=store, client_debts__is_paid=False)
            .annotate(
                total_amount=Sum('client_debts__total_amount'),
                total_deposit=Sum('client_debts__deposit'),
            )
            .order_by('-total_amount')
        )
