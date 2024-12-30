from django.urls import path
from transactions.views import VerfiyTransactionSepView 

urlpatterns = [
    path('verify-transaction-sep/' , VerfiyTransactionSepView.as_view() , name='verify-transaction-sep'),
    path('verify-sep/<str:uuid>/', VerfiyTransactionSepView.as_view(), name='verify-sep'),
]

