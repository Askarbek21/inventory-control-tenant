from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated

from config.permissions import DebtPermission, DebtPaymentPermission
from .serializers import *
from .filters import DebtFilter, DebtPaymentFilter


class DebtViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DebtPermission]
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
