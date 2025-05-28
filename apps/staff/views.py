from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
#from rest_framework_roles.granting import is_self

from .serializers import *


class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    #view_permissions = {
    #    'options': {'admin':True},
    #    'create': {'admin':True},
    #    'list': {'admin':True},
    #    'retrieve': {'admin':True, 'user': is_self},
    #    'update,partial_update': {'admin': True, 'user': is_self},
    #    'destroy': {'admin':True}, 
    #}

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        self.kwargs['pk'] = request.user.id
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)
        else:
            raise NotImplementedError


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
