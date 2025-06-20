from django_filters.rest_framework import DjangoFilterBackend

from config.permissions import TransferPermission
from config.pagination import CustomPageNumberPagination
from .filters import TransferFilter
from .models import Transfer
from .serializers import TransferSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


class TransferViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, TransferPermission]
    serializer_class = TransferSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransferFilter
    pagination_class = (CustomPageNumberPagination)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transfer.objects.all()
        return Transfer.objects.filter(from_stock__store=self.request.user.store)
