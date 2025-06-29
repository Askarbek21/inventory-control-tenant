from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .filters import SponsorFilter
from .serializers import *


class SponsorViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SponsorSerializer
    filterset_class = SponsorFilter
    queryset = Sponsor.objects.all()