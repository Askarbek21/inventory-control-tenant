from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

from config.permissions import IsSelfOrAdmin
from .serializers import *


class UserViewset(viewsets.ModelViewSet):
    permission_classes = [IsSelfOrAdmin]
    serializer_class = UserSerializer

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        self.kwargs['pk'] = request.user.id
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)
        else:
            raise NotImplementedError
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(store=self.request.user.store).select_related('store')


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
