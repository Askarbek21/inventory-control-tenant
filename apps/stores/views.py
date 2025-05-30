from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from config.permissions import StorePermission
from config.pagination import CustomPageNumberPagination
from .serializers import *
from .filters import StoreFilter


class StoreViewset(viewsets.ModelViewSet):
    permission_classes = [StorePermission]
    serializer_class = StoreSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StoreFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(id=self.request.user.store.id)

