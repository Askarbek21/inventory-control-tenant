from rest_framework import viewsets 

from .serializers import *


class DebtViewset(viewsets.ModelViewSet):
    queryset = Debt.objects.select_related('client')
    serializer_class = DebtSerializer


class DebtPaymentViewset(viewsets.ModelViewSet):
    serializer_class = DebtPaymentSerializer

    def get_queryset(self):
        qs = DebtPayment.objects.filter(debt=self.kwargs['debt_pk'])
        return qs
    
