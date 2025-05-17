from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from config.pagination import CustomPageNumberPagination
from .serializers import *
from .filters import StoreFilter


class StoreViewset(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StoreFilter
