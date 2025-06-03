from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets

from config.pagination import CustomPageNumberPagination
from .models import Supplier
from .serializers import SuppliersModelSerializer
from .filters import SupplierFilter


class SuppliersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Supplier.objects.all()
    serializer_class = SuppliersModelSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SupplierFilter
    pagination_class = CustomPageNumberPagination
