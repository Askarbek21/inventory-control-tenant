from django.db.models import Sum, OuterRef, Subquery, F
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from config.pagination import CustomPageNumberPagination
from .filters import LoanFilter, LoanPaymentFilter
from .serializers import *


class LoanViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination
    serializer_class = LoanSerializer
    filterset_class = LoanFilter
    
    def get_queryset(self):
        qs = Loan.objects.filter(sponsor=self.kwargs['sponsor_pk']).select_related('sponsor').prefetch_related('loan_payments')
        return qs

    @action(detail=False, methods=['get'], url_path='grouped-by-currency')
    def grouped_by_currency(self, request, sponsor_pk=None):
        queryset = self.get_queryset().select_related('sponsor')
        grouped = {}

        for loan in queryset:
            currency = loan.currency
            if currency not in grouped:
                grouped[currency] = []
            grouped[currency].append(LoanSerializer(loan).data)

        return Response(grouped)

@action(detail=False, methods=['get'], url_path='totals-by-currency')
def totals_by_currency(self, request, sponsor_pk=None):
    loan_payments_sum_subquery = Subquery(
        LoanPayment.objects.filter(loan=OuterRef('pk'))
        .values('loan')
        .annotate(total_paid_per_loan=Sum('amount'))
        .values('total_paid_per_loan')
    )
    
    queryset = self.get_queryset().annotate(
        total_paid_for_loan=loan_payments_sum_subquery
    ).annotate(
        calculated_remaining_balance=F('total_amount') - F('total_paid_for_loan')
    )

    totals = (
        queryset
        .values('currency')
        .annotate(
            total_loan=Sum('total_amount'),
            total_paid=Sum('total_paid_for_loan'),
            total_unpaid=Sum('calculated_remaining_balance')
        )
    )

    for t in totals:
        t['total_paid'] = t['total_paid'] or 0
        t['total_unpaid'] = t['total_unpaid'] or 0

    return Response(totals)
    

class LoanPaymentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = LoanPaymentSerializer
    filterset_class = LoanPaymentFilter

    def get_queryset(self):
        qs = LoanPayment.objects.filter(loan=self.kwargs['loan_pk'])
        return qs
