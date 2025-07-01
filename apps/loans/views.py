from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from config.pagination import CustomPageNumberPagination
from .filters import LoanFilter, LoanPaymentFilter
from .serializers import *


class LoanViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination
    serializer_class = LoanSerializer
    filterset_class = LoanFilter
    queryset = Loan.objects.select_related('sponsor')


class LoanPaymentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = LoanPaymentSerializer
    filterset_class = LoanPaymentFilter

    def get_queryset(self):
        qs = LoanPayment.objects.filter(loan=self.kwargs['loan_pk'])
        return qs
