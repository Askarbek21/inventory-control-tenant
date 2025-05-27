from rest_framework import viewsets

from .serializers import *
from .filters import SaleFilter


class SaleViewset(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    filterset_class = SaleFilter
    #view_permissions = {
    #    'options': {'admin':True},
    #    'create': {'admin':True, 'seller':True, 'manager':True},
    #    'list': {'admin':True, 'manager':True},
    #    'retrieve': {'admin':True, 'manager': True},
    #    'update,partial_update': {'admin': True},
    #    'destroy': {'admin':True}, 
    #}

    def get_serializer_context(self):
        context = {'request': self.request}
        return context


class SalePaymentViewset(viewsets.ModelViewSet):
    serializer_class = SalePaymentSerializer

    def get_queryset(self):
        qs = SalePayment.objects.filter(sale=self.kwargs['sale_pk'])
        return qs