from rest_framework import viewsets

from .serializers import *


class SaleViewset(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    view_permissions = {
        'options': {'admin':True},
        'create': {'admin':True, 'seller':True, 'manager':True},
        'list': {'admin':True, 'manager':True},
        'retrieve': {'admin':True, 'manager': True},
        'update,partial_update': {'admin': True},
        'destroy': {'admin':True}, 
    }

    def get_serializer_context(self):
        context = {'request': self.request}
        return context
