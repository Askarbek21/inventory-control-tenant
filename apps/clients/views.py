from rest_framework import viewsets

from .serializers import *


class ClientViewset(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

