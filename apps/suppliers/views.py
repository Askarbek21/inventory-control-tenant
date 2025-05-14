from django.shortcuts import render
from rest_framework import viewsets

from .models import Supplier
from .serializers import SuppliersModelSerializer


class SuppliersViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SuppliersModelSerializer
