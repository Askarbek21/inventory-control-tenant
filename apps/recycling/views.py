from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Recycling
from .serializers import RecyclingSerializer
from config.pagination import CustomPageNumberPagination


class RecyclingViewSet(ModelViewSet):
    queryset = Recycling.objects.all()
    serializer_class = RecyclingSerializer
    pagination_class = CustomPageNumberPagination
