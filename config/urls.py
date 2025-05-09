# from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from apps.staff.views import CustomTokenObtainPairView

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('api/v1/store/', include('apps.stores.urls')),
    path('api/v1/personel/', include('apps.staff.urls')),
    path('api/v1/items/', include('apps.items.urls')),
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
