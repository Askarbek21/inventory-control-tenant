# from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from apps.staff.views import CustomTokenObtainPairView
from apps.debts.views import DebtsGroupedByClientView

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('api/v1/store/', include('apps.stores.urls')),
    path('api/v1/users/', include('apps.staff.urls')),
    path('api/v1/items/', include('apps.items.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/debts/', include('apps.debts.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/settings/', include('apps.admin.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/transfer/', include('apps.transfer.urls')),
    path('api/v1/suppliers/', include('apps.suppliers.urls')),
    path('api/v1/recycling/', include('apps.recycling.urls')),
    path('api/v1/budget/', include('apps.expenses.urls')),
    path('api/v1/incomes/', include('apps.incomes.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/debts-by-clients', DebtsGroupedByClientView.as_view()),
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
