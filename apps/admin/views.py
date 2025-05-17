from rest_framework import generics

from .serializers import SiteConfigSerializer, SiteConfig


class UpdateConfigAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteConfigSerializer
    queryset = SiteConfig.objects.all()

    def get_object(self):
        return SiteConfig.get_solo()
    
