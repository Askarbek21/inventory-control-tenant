from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from config.permissions import IsAdministrator
from config.pagination import CustomPageNumberPagination
from .serializers import *
from .filters import IncomeFilter


class IncomeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    pagination_class = CustomPageNumberPagination
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Income.objects.select_related('store')
        return Income.objects.filter(store=self.request.user.store).select_related('store')

        
