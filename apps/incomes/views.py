from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from config.permissions import IsAdministrator
from .serializers import *
from .filters import IncomeFilter


class IncomeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdministrator]
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Income.objects.select_related('store')
        return Income.objects.filter(store=self.request.user).select_related('store')

        
