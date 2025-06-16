from django.db import transaction
from rest_framework import viewsets, generics, response, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from config.permissions import ClientPermission
from .serializers import *
from .services import log_client_balance, pay_debts_from_balance
from .filters import ClientFilter, ClientBalanceFilter


class ClientViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ClientPermission]
    lookup_url_kwarg = 'client_pk'
    serializer_class = ClientSerializer
    filterset_class = ClientFilter
    queryset = Client.objects.all()

    @action(detail=True, methods=['POST'], url_path='increment-balance')
    @transaction.atomic()
    def increment_balance(self, request, client_pk=None):

        client = self.get_object()

        if client.type != 'Юр.лицо':
            return response.Response({'msg': 'Только юр.лица могут пополнять баланс!'}, status.HTTP_400_BAD_REQUEST)
        
        serializer = ClientBalanceIncrementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        old_balance = client.balance
        client.increment_balance(amount)
        log_client_balance(client, old_balance, request=request, new_balance=client.balance)
        pay_debts_from_balance(client, worker=request.user)
        
        return response.Response({'msg': 'Баланс успешно пополнен', 'new_balance': str(client.balance)}, status.HTTP_200_OK)


class ClientBalanceHistoryView(generics.ListAPIView):
    serializer_class = BalanceHistorySerializer
    filterset_class = ClientBalanceFilter

    def get_queryset(self):
        qs = BalanceHistory.objects.filter(client=self.kwargs['client_pk'])
        return qs

