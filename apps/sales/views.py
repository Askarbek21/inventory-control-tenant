from rest_framework import viewsets

from .serializers import *


class SaleViewset(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def get_serializer_context(self):
        context = {'request': self.request}
        return context
