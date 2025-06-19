from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Customer(TenantMixin):
    name = models.CharField(max_length=128)
    created_at = models.DateField(auto_now_add=True)

    auto_create_schema = True

class Domain(DomainMixin):
    pass
