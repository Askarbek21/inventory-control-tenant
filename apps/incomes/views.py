from rest_framework import generics

from .serializers import *
from .filters import IncomeFilter


class IncomeView(generics.ListAPIView):
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    queryset = Income.objects.select_related('store')
        
