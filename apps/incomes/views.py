from rest_framework import generics

from .serializers import *
from .filters import IncomeFilter


class IncomeView(generics.ListAPIView):
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Income.objects.select_related('store')
        return Income.objects.filter(store__owner=self.request.user).select_related('store', 'store__owner')

        
