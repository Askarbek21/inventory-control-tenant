from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.items.serializers import *
from config.pagination import CustomPageNumberPagination
from config.permissions import ItemPermission, StockPermission
from .filters import *
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ItemPermission]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CategoryFilter


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ItemPermission]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    

         

class MeasurementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ItemPermission]
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MeasurementFilter


class CurrencyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ItemPermission]
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    pagination_class = CustomPageNumberPagination
    http_method_names = ['get', 'post', 'put', 'patch']


class StockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, StockPermission]
    serializer_class = StockSerializers
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StockFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Stock.objects.all()
        return Stock.objects.filter(store=self.request.user.store)
