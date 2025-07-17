from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recycling
from .serializers import RecyclingSerializer
from config.pagination import CustomPageNumberPagination
from config.permissions import RecyclingPermission
from .filters import RecyclingFilter

class RecyclingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, RecyclingPermission]
    serializer_class = RecyclingSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecyclingFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Recycling.objects.all()
        return Recycling.objects.filter(from_to__store=self.request.user.store)
