from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Payment
from stock_affairs.models import Underwriting
from transactions.sep import SEPOnlinePayment
from rest_framework.exceptions import ValidationError
from django.utils import timezone


# SEP
class VerfiyTransactionSepView(APIView):
    def post(self, request, uuid):
        # دریافت پارامترهای برگشتی از بانک از query parameters
        invoice_unique_id = uuid
        MID = request.data.get('MID')  # شماره ترمینال
        RefNum = request.data.get('RefNum') # رسید دیجیتالی خرید
        State = request.data.get('State') # وضعیت تراکنش
        Status = request.data.get('Status') # وضعیت تراکنش
        RRN = request.data.get('RRN') # شماره مرجع
        TraceNo = request.data.get('TraceNo') # شماره پیگیری
        HashedCardNumber = request.data.get('HashedCardNumber') # شماره کارت هش شده
        SecurePan = request.data.get('SecurePan') # شماره کارت  
        Wage = request.data.get('Wage') # عملیات
        Amount = request.data.get('Amount') # مبلغ

        if not invoice_unique_id:
            return Response(
                {"error": "شناسه فاکتور الزامی است"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment = Payment.objects.get(invoice_unique_id=invoice_unique_id)
        
        if Status in ['1','3','4','5','6','7','8','9','10','11','12']:
            success = False
            payment.status = 'rejected'
            payment.error_code = Status
            payment.error =State
            payment.verify_transaction = True
            payment.updated_at = timezone.now()
            payment.save()

        elif Status in ['2']:
            success = True
            sep = SEPOnlinePayment(
                payment.payment_gateway,
                invoice_unique_id=invoice_unique_id
            )
            verification_result = sep.verify_transaction(RefNum)
            data = verification_result.get('TransactionDetail', {})
            if RRN:
                payment.refrence_number = RRN
            else:
                payment.refrence_number = data.get('RRN')
            payment.verify_transaction = True
            payment.cart_number = SecurePan
            payment.hashed_cart_number = HashedCardNumber
            payment.track_id = TraceNo
            payment.status = 'approved'
            payment.save()

        return redirect(f'http://localhost:5173/paymentresult?success={success}')
        
        






        
