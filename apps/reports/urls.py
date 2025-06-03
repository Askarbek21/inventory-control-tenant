from django.urls import path

from .views import *

urlpatterns = [
    path('sales-summary/', SalesSummaryView.as_view()),
    path('top-products/', TopProductsView.as_view()),
    path('unsold-products/', UnsoldProductsView.as_view()),
    path('stock-by-category/', StockByCategoryView.as_view()),
    path('product-intake/', ProductIntakeView.as_view()),
    path('product-profitability/', ProductProfitabilityView.as_view()),
    path('client-debts/', ClientDebtView.as_view()),
    path('top-sellers/', TopSellersView.as_view()),
    path('salesman-summary/', SalesmanSummaryView.as_view()),
    path('salesman-debts/', SalesmanDebtView.as_view()),
    path('expenses-summary/', ExpenseSummaryView.as_view()),
]
