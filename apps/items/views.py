
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from apps.items.serializers import *
from config.pagination import CustomPageNumberPagination
from .filters import *


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CategoryFilter


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MeasurementFilter


class StockViewSet(viewsets.ModelViewSet):

    serializer_class = StockSerializers
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StockFilter
    def get_queryset(self):
        user = self.request.user
        queryset = Stock.objects.filter(store__owner=user.id)
        return queryset

