from rest_framework import views, response, status
from django.db.models import Sum

from apps.sales.models import Sale
from apps.debts.models import Debt


class ReportAPIView(views.APIView):
    def get(self, *args, **kwargs):
        total_income = Sale.objects.filter(sale_debt__is_paid=True).aggregate(total_income=Sum('total_amount'))['total_income']
        total_unpaid_debts = Debt.objects.filter(is_paid=False).aggregate(total_unpaid=Sum('total_amount'))['total_unpaid']
        
        data = {
            'total_income': total_income,
            'total_unpaid_debts': total_unpaid_debts
        }
        return response.Response(data, status=status.HTTP_200_OK)
    
