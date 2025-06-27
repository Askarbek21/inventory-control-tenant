from django.http import JsonResponse
from django_tenants.utils import get_tenant

def debug_tenant_view(request):
    tenant = get_tenant(request)
    return JsonResponse({
        "host_header": request.get_host(),
        "tenant_name": tenant.name,
        "schema": tenant.schema_name,
    })
