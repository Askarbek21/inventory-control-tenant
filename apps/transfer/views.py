
from django.shortcuts import render

from config.pagination import CustomPageNumberPagination
from .models import Transfer
# Create your views here.
from .serializers import TransferSerializer
from rest_framework.viewsets import ModelViewSet


class TransferViewSet(ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    pagination_class = (
        CustomPageNumberPagination)

