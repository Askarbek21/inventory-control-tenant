from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from config.permissions import StorePermission
from config.pagination import CustomPageNumberPagination
from .serializers import *
from .filters import StoreFilter


class StoreViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, StorePermission]
    serializer_class = StoreSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StoreFilter

    queryset = Store.objects.all()

