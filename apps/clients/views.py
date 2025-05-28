from rest_framework import viewsets, generics

from .serializers import *
from .filters import ClientFilter, ClientBalanceFilter


class ClientViewset(viewsets.ModelViewSet):
    lookup_url_kwarg = 'client_pk'
    serializer_class = ClientSerializer
    filterset_class = ClientFilter
    queryset = Client.objects.all()
    

class ClientBalanceHistoryView(generics.ListAPIView):
    serializer_class = BalanceHistorySerializer
    filterset_class = ClientBalanceFilter

    def get_queryset(self):
        qs = BalanceHistory.objects.filter(client=self.kwargs['client_pk'])
        return qs

