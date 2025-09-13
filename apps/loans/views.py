from collections import defaultdict
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
        qs = Loan.objects.filter(sponsor=self.kwargs['sponsor_pk']).select_related('sponsor')
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
        queryset = self.get_queryset().prefetch_related('loan_payments')

        results = defaultdict(lambda: {
            "total_loan": 0,
            "total_paid": 0,
            "total_unpaid": 0,
        })

        for loan in queryset:
            currency = loan.currency
            total_paid = sum(p.amount for p in loan.loan_payments.filter(is_overflowed=False))

            results[currency]["total_loan"] += float(loan.total_amount)
            results[currency]["total_paid"] += float(total_paid)
            results[currency]["total_unpaid"] += float(loan.remaining_balance)

        response = [
            {"currency": currency, **totals}
            for currency, totals in results.items()
        ]
        return Response(response)


class LoanPaymentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = LoanPaymentSerializer
    filterset_class = LoanPaymentFilter

    def get_queryset(self):
        qs = LoanPayment.objects.filter(loan=self.kwargs['loan_pk'])
        return qs
