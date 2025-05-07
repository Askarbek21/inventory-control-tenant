from rest_framework import viewsets

from .serializers import *


class StoreViewset(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    
