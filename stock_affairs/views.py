from django.shortcuts import render
from rest_framework import viewsets
from .models import Shareholders , StockTransfer , Precedence , CapitalIncreasePayment , DisplacementPrecedence , Underwriting , UnusedPrecedenceProcess
from rest_framework.permissions import IsAuthenticated , IsAdminUser 
from .serializers import ShareholdersSerializer , StockTransferSerializer , PrecedenceSerializer , CapitalIncreasePaymentSerializer , DisplacementPrecedenceSerializer , UnderwritingSerializer , UnusedPrecedenceProcessSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.exceptions import ValidationError
from stock_affairs.permission import IsShareholder , IsPrecedence , IsUnderwriting , IsUnusedPrecedenceProcess
from django.db import transaction
from django.utils import timezone
from django.db import models
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from rest_framework.views import APIView
import uuid
from transactions.sep import SEPOnlinePayment
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from transactions.models import Payment

class ShareholdersViewset(viewsets.ModelViewSet):
    queryset = Shareholders.objects.all()
    serializer_class = ShareholdersSerializer
    permission_classes = [IsAuthenticated , IsShareholder | IsAdminUser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif not self.request.user.is_staff:
            self.queryset = Shareholders.objects.filter(user=self.request.user)
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        try:
            number_of_shares = int(request.data.get('number_of_shares', 0))
            if number_of_shares < 0:
                raise ValidationError({"error": "تعداد سهام نمی‌تواند منفی باشد"})
        except (ValueError, TypeError):
            raise ValidationError({"error": "تعداد سهام باید یک عدد صحیح باشد"})
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        if request.data.get('number_of_shares', 0) < 0:
            raise ValidationError({"error": "تعداد سهام نمی‌تواند منفی باشد"})
        return super().partial_update(request, *args, **kwargs)


class StockTransferViewset(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif not self.request.user.is_staff:
            self.queryset = StockTransfer.objects.filter(
                Q(buyer=self.request.user) | Q(seller=self.request.user)
            )
        return super().get_permissions()
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # بررسی موجودی سهام فروشنده
        seller_shares = Shareholders.objects.filter(user=serializer.validated_data['seller'],company=serializer.validated_data['company']).first()
        
        if not seller_shares or seller_shares.number_of_shares < serializer.validated_data['number_of_shares']:
            raise ValidationError({"error": "تعداد سهام فروشنده کافی نیست"})

        # ذخیره انتقال سهام
        self.perform_create(serializer)
        
        # به‌روزرسانی سهام فروشنده
        seller_shares.number_of_shares -= serializer.validated_data['number_of_shares']
        seller_shares.save()
        
        # به‌روزرسانی یا ایجاد سهام خریدار
        buyer_shares = Shareholders.objects.filter(user=serializer.validated_data['buyer'],company=serializer.validated_data['company']).first()
        
        if buyer_shares:
            buyer_shares.number_of_shares += serializer.validated_data['number_of_shares']
            buyer_shares.save()
        else:
            Shareholders.objects.create(
                user=serializer.validated_data['buyer'],
                company=serializer.validated_data['company'],
                number_of_shares=serializer.validated_data['number_of_shares']
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        if request.user.is_staff:
            try:
                instance = self.get_object()
                old_number_of_shares = instance.number_of_shares
                
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                
                new_number_of_shares = serializer.validated_data.get('number_of_shares')
                
                if new_number_of_shares is None:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                difference = new_number_of_shares - old_number_of_shares
                
                if difference != 0:
                    seller_shares = Shareholders.objects.select_for_update().get(
                        user=instance.seller,
                        company=instance.company
                    )
                    
                    buyer_shares = Shareholders.objects.select_for_update().get(
                        user=instance.buyer,
                        company=instance.company
                    )
                    
                    if difference > 0:  # افزایش تعداد سهام
                        if seller_shares.number_of_shares < difference:
                            raise ValidationError({"error": "تعداد سهام فروشنده کافی نیست"})
                        seller_shares.number_of_shares -= difference
                        buyer_shares.number_of_shares += difference
                    else:  # کاهش تعداد سهام
                        seller_shares.number_of_shares += abs(difference)
                        buyer_shares.number_of_shares -= abs(difference)
                    
                    seller_shares.updated_at = timezone.now()
                    buyer_shares.updated_at = timezone.now()
                    seller_shares.save()
                    buyer_shares.save()
                    
                    instance.number_of_shares = new_number_of_shares
                    instance.updated_at = timezone.now()
                    instance.save()
                
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Shareholders.DoesNotExist:
                return Response(
                    {"error": "سهامدار مورد نظر یافت نشد"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "شما اجازه ویرایش را ندارید"}, 
                status=status.HTTP_403_FORBIDDEN
            )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        if request.user.is_staff:
            try:
                instance = self.get_object()
                
                # بازگرداندن سهام به فروشنده و کم کردن از خریدار
                seller_shares = Shareholders.objects.select_for_update().get(
                    user=instance.seller,
                    company=instance.company
                )
                
                buyer_shares = Shareholders.objects.select_for_update().get(
                    user=instance.buyer,
                    company=instance.company
                )
                
                # برگرداندن سهام به فروشنده
                seller_shares.number_of_shares += instance.number_of_shares
                # کم کردن سهام از خریدار
                buyer_shares.number_of_shares -= instance.number_of_shares
                
                seller_shares.save()
                buyer_shares.save()
                
                # حذف رکورد انتقال سهام
                instance.delete()
                
                return Response(
                    {"message": "انتقال سهام با موفقیت حذف شد"}, 
                    status=status.HTTP_204_NO_CONTENT
                )
                
            except Shareholders.DoesNotExist:
                return Response(
                    {"error": "سهامدار مورد نظر یافت نشد"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "شما اجازه حذف را ندارید"}, 
                status=status.HTTP_403_FORBIDDEN
            )


class PrecedenceViewset(viewsets.ModelViewSet):
    queryset = Precedence.objects.all()
    serializer_class = PrecedenceSerializer
    permission_classes = [IsAuthenticated, IsPrecedence]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            queryset = self.get_queryset().filter(user=request.user)
            
            precedence_totals = (
                CapitalIncreasePayment.objects
                .filter(precedence__user=request.user)
                .annotate(total_precedence=Sum('amount'))
            )
            
            totals_dict = {item['precedence__company']: item['total_precedence'] for item in precedence_totals}
            
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
            for item in data:
                item['total_precedence'] = totals_dict.get(item['company'], 0)
            
            return Response(data)
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
            precedence_totals = (
                CapitalIncreasePayment.objects
                .values('precedence__company')
                .annotate(total_precedence=Sum('amount'))
            )
            totals_dict = {item['precedence__company']: item['total_precedence'] for item in precedence_totals}
            
            for item in data:
                item['total_precedence'] = totals_dict.get(item['company'], 0)
                
            return Response(data)
    

class CapitalIncreasePaymentViewset(viewsets.ModelViewSet):
    queryset = CapitalIncreasePayment.objects.all()
    serializer_class = CapitalIncreasePaymentSerializer
    permission_classes = [IsAuthenticated, IsPrecedence]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def _check_amount_validity(self, precedence, new_amount, instance=None):
        # محاسبه مجموع پرداخت‌های قبلی
        total_previous_payments = CapitalIncreasePayment.objects.filter(
            precedence=precedence
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        # اگر در حال آپدیت هستیم، مقدار فعلی را از مجموع کم می‌کنیم
        if instance:
            total_previous_payments -= instance.amount

        # محاسبه مقدار باقی‌مانده
        remaining_precedence = precedence.precedence - total_previous_payments

        # بررسی اینکه آیا مقدار درخواستی از باقی‌مانده بیشتر است
        if new_amount > remaining_precedence:
            raise ValidationError({
                "error": f"مقدار درخواستی ({new_amount}) از مقدار باقی‌مانده حق تقدم ({remaining_precedence}) بیشتر است"
            })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        precedence = serializer.validated_data['precedence']
        new_amount = serializer.validated_data['amount']

        self._check_amount_validity(precedence, new_amount)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # اگر مقدار amount تغییر کرده باشد، بررسی اعتبارسنجی را انجام می‌دهیم
        if 'amount' in serializer.validated_data:
            new_amount = serializer.validated_data['amount']
            precedence = serializer.validated_data.get('precedence', instance.precedence)
            self._check_amount_validity(precedence, new_amount, instance)

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_str = str(instance)  # ذخیره اطلاعات قبل از حذف
        
        self.perform_destroy(instance)
        
        return Response({
            "message": f"پرداخت حق تقدم {instance_str} با موفقیت حذف شد",
            "status": "success"
        }, status=status.HTTP_200_OK)


class DisplacementPrecedenceViewset(viewsets.ModelViewSet):
    queryset = DisplacementPrecedence.objects.all()
    serializer_class = DisplacementPrecedenceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # بررسی موجودی حق تقدم فروشنده
        seller_precedence = Precedence.objects.filter(user=serializer.validated_data['seller'],company=serializer.validated_data['company']).first()
        
        if not seller_precedence or seller_precedence.precedence < serializer.validated_data['number_of_shares']:
            raise ValidationError({"error": "تعداد حق تقدم فروشنده کافی نیست"})

        # ذخیره انتقال حق تقدم
        self.perform_create(serializer)
        
        # به‌روزرسانی حق تقدم فروشنده
        seller_precedence.precedence -= serializer.validated_data['number_of_shares']
        seller_precedence.save()
        
        # به‌روزرسانی یا ایجاد حق تقدم خریدار
        buyer_precedence = Precedence.objects.filter(user=serializer.validated_data['buyer'],company=serializer.validated_data['company']).first()
        
        if buyer_precedence:
            buyer_precedence.precedence += serializer.validated_data['number_of_shares']
            buyer_precedence.save()
        else:
            Precedence.objects.create(
                user=serializer.validated_data['buyer'],
                company=serializer.validated_data['company'],
                precedence=serializer.validated_data['number_of_shares'],
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        if request.user.is_staff:
            try:
                instance = self.get_object()
                old_number_of_shares = instance.number_of_shares
                
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                
                new_number_of_shares = serializer.validated_data.get('number_of_shares')
                
                if new_number_of_shares is None:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                difference = new_number_of_shares - old_number_of_shares
                
                if difference != 0:
                    seller_precedence = Precedence.objects.select_for_update().filter(
                        user=instance.seller,
                        company=instance.company
                    ).first()
                    
                    buyer_precedence = Precedence.objects.select_for_update().filter(
                        user=instance.buyer,
                        company=instance.company
                    ).first()
                    
                    if not seller_precedence or not buyer_precedence:
                        raise Precedence.DoesNotExist
                    
                    if difference > 0:  # افزایش تعداد حق تقدم
                        if seller_precedence.precedence < difference:
                            raise ValidationError({"error": "تعداد حق تقدم فروشنده کافی نیست"})
                        seller_precedence.precedence -= difference
                        buyer_precedence.precedence += difference
                    else:  # کاهش تعداد حق تقدم
                        seller_precedence.precedence += abs(difference)
                        buyer_precedence.precedence -= abs(difference)
                    
                    seller_precedence.updated_at = timezone.now()
                    buyer_precedence.updated_at = timezone.now()
                    seller_precedence.save()
                    buyer_precedence.save()
                    
                    instance.number_of_shares = new_number_of_shares
                    instance.updated_at = timezone.now()
                    instance.save()
                
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Precedence.DoesNotExist:
                return Response(
                    {"error": "حق تقدم مورد نظر یافت نشد"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "شما اجازه ویرایش را ندارید"}, 
                status=status.HTTP_403_FORBIDDEN
            )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        if request.user.is_staff:
            try:
                instance = self.get_object()
                
                # بازگرداندن سق تقدم به فروشنده و کم کردن از خریدار
                seller_precedence = Precedence.objects.select_for_update().get(
                    user=instance.seller,
                    company=instance.company
                )
                
                buyer_precedence = Precedence.objects.select_for_update().get(
                    user=instance.buyer,
                    company=instance.company
                )
                
                # برگرداندن سق تقدم به فروشنده
                seller_precedence.precedence += instance.number_of_shares
                # کم کردن حق تقدم از خریدار
                buyer_precedence.precedence -= instance.number_of_shares
                
                seller_precedence.save()
                buyer_precedence.save()
                
                # حذف رکورد انتقال حق تقدم
                instance.delete()
                
                return Response(
                    {"message": "انتقال حق تقدم با موفقیت حذف شد"}, 
                    status=status.HTTP_204_NO_CONTENT
                )
                
            except Precedence.DoesNotExist:
                return Response(
                    {"error": "حق تقدم مورد نظر یافت نشد"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "شما اجازه حذف را ندارید"}, 
                status=status.HTTP_403_FORBIDDEN
            )


#  خرید حق تقدم استفاده نشده ایجاد کنید
class CreateUnderwritingViewset(APIView):
    permission_classes = [IsAuthenticated, IsUnusedPrecedenceProcess]
    http_method_names = ['get', 'post', 'patch', 'put']
    
    def get_permissions(self):
        return [permission() for permission in self.permission_classes]
    
    def get(self, request, pk=None):
        if pk:
            if request.user.is_staff:
                underwriting = get_object_or_404(Underwriting, id=pk)
            else:
                underwriting = get_object_or_404(Underwriting, id=pk, user=request.user)
            serializer = UnderwritingSerializer(underwriting)
            return Response(serializer.data)
        
        if request.user.is_staff:
            underwritings = Underwriting.objects.all()
        else:
            underwritings = Underwriting.objects.filter(user=request.user)
        

            
        underwritings = underwritings.order_by('-created_at')
        
        serializer = UnderwritingSerializer(underwritings, many=True)
        return Response(serializer.data)

    def post(self, request):
        process_id = request.data.get('process')
        amount = request.data.get('amount')
        payment_type = request.data.get('type')
        
        # بررسی وجود همه فیلدهای ضروری
        if not all([process_id, amount, payment_type]):
            raise ValidationError({"error": "تمامی فیلدهای process، amount و type الزامی هستند"})

        # بررسی و دریافت فرآیند
        process = UnusedPrecedenceProcess.objects.filter(id=process_id, is_active=True).first()
        if not process:
            raise ValidationError({"error": "فرآیند فعال یافت نشد"})

        try:
            amount = int(amount)
            value = amount * process.price
        except (ValueError, TypeError):
            raise ValidationError({"error": "مقدار amount باید عددی صحیح باشد"})

        # بررسی موجودی
        if amount > process.used_amount: 
            raise ValidationError({"error": "مقدار درخواستی بیشتر از موجودی است"})

        invoice_unique_id=str(uuid.uuid4())
        # ایجاد خرید
        underwriting = Underwriting.objects.create(
            user=request.user,
            process=process,
            requested_amount=amount,
            price=value,
            type=payment_type,
            
        )

        if payment_type == '2':  # پرداخت آنلاین
            try:
                payment_gateway = process.payment_gateway
                sep = SEPOnlinePayment(payment_gateway , invoice_unique_id=invoice_unique_id)
                token_response = sep.request_token(
                    value,
                    invoice_unique_id,
                    request.user.mobile
                )

                if token_response['status'] == -1:
                    underwriting.delete()  # حذف خرید در صورت خطا
                    raise ValidationError({"error": "خطا در ایجاد تراکنش"})

                payment_url = sep.redirect_to_payment(token_response['token'])
                transaction = Payment.objects.create(
                    payment_gateway=payment_gateway,
                    invoice_unique_id=invoice_unique_id,
                    transaction_url=payment_url,
                    status='pending'
                )
                transaction.save()
                underwriting.payment = transaction
                underwriting.save()

                return Response({'redirect_url': payment_url}, status=status.HTTP_200_OK)

            except Exception as e:
                raise ValidationError({"error": f"خطا در پردازش پرداخت: {str(e)}"})

        elif payment_type == '1':  # پرداخت با فیش
            if not request.FILES.get('document'):
                raise ValidationError({"error": "آپلود فیش پرداخت الزامی است"})
            
            underwriting.document = request.FILES['document']
            underwriting.save()
            return Response({"message": "خرید با موفقیت ثبت شد"}, status=status.HTTP_201_CREATED)
        
        else:
            raise ValidationError({"error": "نوع پرداخت نامعتبر است"})

    def patch(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"error": "شما دسترسی لازم را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if not new_status:
            raise ValidationError({"error": "وضعیت جدید الزامی است"})
        
        underwriting = get_object_or_404(Underwriting, id=pk)
        if underwriting.type == '1':
            # underwriting.status = new_status
            underwriting.updated_at = timezone.now()
            underwriting.save()
        else:
            # underwriting.payment.status = new_status
            underwriting.payment.updated_at = timezone.now()
            underwriting.payment.save()
        serializer = UnderwritingSerializer(underwriting)

        return Response({"message" : "وضعیت خرید با موفقیت به‌روزرسانی شد","data" : serializer.data },  status=status.HTTP_200_OK)


class UnusedPrecedenceProcessViewset(viewsets.ModelViewSet):
    queryset = UnusedPrecedenceProcess.objects.all()
    serializer_class = UnusedPrecedenceProcessSerializer
    permission_classes = [IsAuthenticated , IsUnusedPrecedenceProcess]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(is_active=True)





