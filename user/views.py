from django.shortcuts import render
from rest_framework.views import APIView
from GuardPyCaptcha.Captch import GuardPyCaptcha
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from rest_framework import status
from .models import User , Otp , legalPersonStakeholders , legalPersonShareholders , AgentUser,  LegalPerson , JobInfo , Addresses ,Accounts , UUid , CodeForgotPassword
from rest_framework.permissions import AllowAny,IsAuthenticated , IsAdminUser
import json
import requests
import os
from space_api import settings
from django.utils import timezone
from .serializers import UUidSerializer , UserSerializer , AccountsSerializer , AddressesSerializer , JobInfoSerializer , AgentUserSerializer ,LegalPersonSerializer , legalPersonShareholdersSerializer , legalPersonStakeholdersSerializer , CodeForgotPasswordSerializer
from .date import parse_date
from datetime import timedelta
from uuid import uuid4
from utils.legal import is_legal_person
from rest_framework_simplejwt.tokens import RefreshToken 
import random
from utils.notification_service import NotificationService
import logging
from timeflow.models import UserLoginLog
logger = logging.getLogger(__name__)

# otp sejam
class OtpSejamViewset(APIView):
    permission_classes = [AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request):
        encrypted_response = request.data['encrypted_response'].encode()
        if isinstance(encrypted_response, str):
            encrypted_response = encrypted_response.encode('utf-8')
        captcha = GuardPyCaptcha()

        captcha = captcha.check_response(encrypted_response, request.data['captcha'])
        if request.data['captcha'] == ''  or not captcha :
            pass#return Response ({'message' : 'کد کپچا خالی است'} , status=status.HTTP_400_BAD_REQUEST)

        uniqueIdentifier = request.data['uniqueIdentifier']
        if not uniqueIdentifier :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter (uniqueIdentifier = uniqueIdentifier,is_sejam_registered=True).first()
        if not user:
            url = "http://31.40.4.92:8870/otp"
            payload = json.dumps({
            "uniqueIdentifier": uniqueIdentifier
            })
            headers = {
            'X-API-KEY': "zH7n^K8s#D4qL!rV9tB@2xEoP1W%0uNc" ,#os.getenv('X-API-KEY','zH7n^K8s#D4qL!rV9tB@2xEoP1W%0uNc'),
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)

            logger.info(f"uniqueIdentifier: {uniqueIdentifier}")
            logger.info(f"response content: {response.content}")  
            logger.info(f"status code: {response.status_code}")
            if response.status_code >=300 :
                return Response ({'message' :'شما سجامی نیستید'} , status=status.HTTP_400_BAD_REQUEST)
            return Response ({'registered' :False , 'message' : 'کد تایید ارسال شد'},status=status.HTTP_200_OK)

        return Response({'message' : 'شما قبلا ثبت نام کرده اید'},status=status.HTTP_400_BAD_REQUEST)   
                

# register  user's account for new user
class RegisterViewset(APIView):
    permission_classes = [AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self, request) :
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        otp = request.data.get('otp')
        user = None

        if not uniqueIdentifier or not otp:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user :
            url = "http://31.40.4.92:8870/information"
            payload = json.dumps({
            "uniqueIdentifier": uniqueIdentifier,
            "otp": otp
            })
            headers = {
            'X-API-KEY':'zH7n^K8s#D4qL!rV9tB@2xEoP1W%0uNc', #os.getenv('X-API-KEY'),
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = json.loads(response.content)
            try :
                data = response['data']
            except:
                return Response({'message' :'1دوباره تلاش کن '}, status=status.HTTP_400_BAD_REQUEST)
            if data == None :
                return Response({'message' :'بیشتر تلاش کن '}, status=status.HTTP_400_BAD_REQUEST)
            new_user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
            private_person_data = data['privatePerson']
            if not new_user :
               
                new_user, created = User.objects.update_or_create(
                    uniqueIdentifier=uniqueIdentifier,
                    defaults={
                        'username': uniqueIdentifier,
                        'email': data.get('email'),
                        'is_active': True,
                        'first_name': private_person_data.get('firstName'),
                        'last_name': private_person_data.get('lastName'),
                        'mobile': data.get('mobile'),
                        'gender': 'M' if private_person_data.get('gender') == 'Male' else 'F' if private_person_data.get('gender') == 'Female' else None,
                        'birth_date': parse_date(private_person_data.get('birthDate')),
                        'created_at': parse_date(data.get('createdAt')),
                        'updated_at': parse_date(data.get('updatedAt')),
                        'address': data['addresses'][0].get('remnantAddress') if data.get('addresses') and len(data['addresses']) > 0 else None,
                        'profile_image': None,
                        'last_login': None,
                        'status': True if data.get('status') == 'Sejami' else False,
                        'bio': None,
                        'chat_id_telegram': None,
                        'last_password_change': None,
                        'login_attempts': 0,
                        'seri_shenasname': private_person_data.get('seriSh'),
                        'seri_shenasname_char': private_person_data.get('seriShChar'),
                        'serial_shenasname': private_person_data.get('serial'),
                        'place_of_birth': private_person_data.get('placeOfBirth'),
                        'place_of_issue': private_person_data.get('placeOfIssue'),
                        'father_name': private_person_data.get('fatherName'),
                        'education_level': None,
                        'marital_status': None,
                        'is_sejam_registered': True,
                    }
                )
                new_user = User.objects.get(uniqueIdentifier=data.get('uniqueIdentifier'))
                password = random.randint(100000, 999999)
                print(password)
                new_user.set_password(str(password))
                new_user.save()
                
            if len(data['legalPersonStakeholders']) > 0:
                    for legalPersonStakeholders_data in data['legalPersonStakeholders'] :
                        new_legalPersonStakeholders = legalPersonStakeholders(
                        user = new_user ,
                        uniqueIdentifier =legalPersonStakeholders_data['uniqueIdentifier'] ,
                        type = legalPersonStakeholders_data['type'],
                        start_at = legalPersonStakeholders_data ['startAt'],
                        position_type = legalPersonStakeholders_data ['positionType'],
                        last_name = legalPersonStakeholders_data ['lastName'],
                        is_owner_signature = legalPersonStakeholders_data ['isOwnerSignature'],
                        first_name = legalPersonStakeholders_data ['firstName'],
                        end_at = legalPersonStakeholders_data ['endAt'] ,)
                    new_legalPersonStakeholders.save()

            if data['legalPerson']:
                new_LegalPerson = LegalPerson(
                user = new_user ,
                company_name = data['legalPerson']['companyName'] ,
                citizenship_country =data['legalPerson']['citizenshipCountry'] ,
                economic_code = data['legalPerson']['economicCode'],
                evidence_expiration_date = data['legalPerson'] ['evidenceExpirationDate'],
                evidence_release_company = data['legalPerson'] ['evidenceReleaseCompany'],
                evidence_release_date = data['legalPerson'] ['evidenceReleaseDate'],
                legal_person_type_sub_category = data['legalPerson'] ['legalPersonTypeSubCategory'],
                register_date = data['legalPerson'] ['registerDate'],
                legal_person_type_category = data['legalPerson'] ['legalPersonTypeCategory'],
                register_place = data['legalPerson'] ['registerPlace'] ,
                register_number = data['legalPerson'] ['registerNumber'] ,)
                new_LegalPerson.save()

            if len(data['legalPersonShareholders']) > 0:
                    for legalPersonShareholders_data in data['legalPersonShareholders'] :
                        new_legalPersonShareholders = legalPersonShareholders(
                        user = new_user ,
                        uniqueIdentifier = legalPersonShareholders_data['uniqueIdentifier'],
                        postal_code = legalPersonShareholders_data ['postalCode'],
                        position_type = legalPersonShareholders_data ['positionType'],
                        percentage_voting_right = legalPersonShareholders_data ['percentageVotingRight'],
                        first_name = legalPersonShareholders_data ['firstName'],
                        last_name = legalPersonShareholders_data ['lastName'],
                        address = legalPersonShareholders_data ['address'] )
                    new_legalPersonShareholders.save()
            if len(data['accounts']) > 0:
                for acounts_data in data['accounts'] :
                    new_accounts = Accounts(
                        user = new_user ,
                        account_number = acounts_data['accountNumber'] ,
                        bank = acounts_data ['bank']['name'],
                        branch_code = acounts_data ['branchCode'],
                        branch_name = acounts_data ['branchName'],
                        is_default = acounts_data ['isDefault'],
                        type = acounts_data ['type'],
                        sheba_number = acounts_data ['sheba'] ,)
                    new_accounts.save()
            if len (data['addresses']) > 0 :
                for addresses_data in data ['addresses']:
                    new_addresses = Addresses (
                        user = new_user,
                        alley =  addresses_data ['alley'],
                        city =  addresses_data ['city']['name'],
                        city_prefix =  addresses_data ['cityPrefix'],
                        country = addresses_data ['country']['name'],
                        country_prefix =  addresses_data ['countryPrefix'],
                        email =  addresses_data ['email'],
                        emergency_tel =  addresses_data ['emergencyTel'],
                        emergency_tel_city_prefix =  addresses_data ['emergencyTelCityPrefix'],
                        emergency_tel_country_prefix =  addresses_data ['emergencyTelCountryPrefix'],
                        fax =  addresses_data ['fax'],
                        fax_prefix =  addresses_data ['faxPrefix'],
                        plaque =  addresses_data ['plaque'],
                        postal_code =  addresses_data ['postalCode'],
                        province =  addresses_data ['province']['name'],
                        remnant_address =  addresses_data ['remnantAddress'],
                        section =  addresses_data ['section']['name'],
                        tel =  addresses_data ['tel'],
                    )
                    new_addresses.save()
                jobInfo_data = data.get('jobInfo')
                if isinstance(jobInfo_data, dict):
                    employment_date = request.data.get('employmentDate')
                    if employment_date is not None:

                        employment_date = employment_date.split('T')[0]  # 1346 the date format

                    new_jobInfo = JobInfo(
                        user=new_user,
                        company_address=jobInfo_data.get('companyAddress', ''),
                        company_city_prefix=jobInfo_data.get('companyCityPrefix', ''),
                        company_email=jobInfo_data.get('companyEmail', ''),
                        company_fax=jobInfo_data.get('companyFax', ''),
                        company_fax_prefix=jobInfo_data.get('companyFaxPrefix', ''),
                        company_name=jobInfo_data.get('companyName', ''),
                        company_phone=jobInfo_data.get('companyPhone', ''),
                        company_postal_code=jobInfo_data.get('companyPostalCode', ''),
                        company_web_site=jobInfo_data.get('companyWebSite', ''),
                        employment_date=employment_date,
                        job_title=jobInfo_data.get('job', {}).get('title', ''),
                        job_description=jobInfo_data.get('jobDescription', ''),
                        position=jobInfo_data.get('position', ''),
                    )

                    new_jobInfo.save()
                agent = data.get('agent')
                if isinstance(agent, dict):
                    new_agent = AgentUser(
                        user=new_user,
                        description=new_agent.get('description', ''),
                        expiration_date=new_agent.get('expirationDate', ''),
                        first_name=new_agent.get('firstName', ''),
                        is_confirmed=new_agent.get('isConfirmed', ''),
                        last_name=new_agent.get('lastName', ''),
                        type=new_agent.get('type', ''),
                        father_uniqueIdentifier=new_agent.get('uniqueIdentifier', ''),
     
                    )

                    new_agent.save()
            
            refresh = RefreshToken.for_user(new_user)
            access = str(refresh.access_token)
            notification_service = NotificationService()
            notification_service.send_sms(to = str(new_user.mobile), message=str(password), template='set_password')

            user_agent = request.META.get('HTTP_USER_AGENT', '')
            # استخراج اطلاعات به صورت ایمن
            try:
                device_type = user_agent.split('/')[0] if '/' in user_agent else 'Unknown'
                browser = user_agent.split('/')[-1] if '/' in user_agent else 'Unknown'
                os_type = user_agent.split('(')[1].split(')')[0] if '(' in user_agent and ')' in user_agent else 'Unknown'
            except:
                device_type = 'Unknown'
                browser = 'Unknown'
                os_type = 'Unknown'

            # ثبت لاگ ثبت نام
            UserLoginLog.objects.create(
                user=new_user,
                type='register',
                ip_address=request.META.get('REMOTE_ADDR'),
                device_type=device_type,
                browser=browser,
                os_type=os_type
            )

            return Response({'refresh': str(refresh), 'access':access}, status=status.HTTP_200_OK)


#update user password
class ChangePasswordViewset(APIView):
    permission_classes = [IsAuthenticated]
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def patch(self, request):
        user = request.user
        last_password = request.data.get('last_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        if not last_password or not new_password or not new_password_confirm:
            return Response({'message': 'اطلاعات وارد شده نادرست است'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != new_password_confirm:
            return Response({'message': 'رمز عبور وارد شده با تکرار آن مطابقت ندارد'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(last_password):
            return Response({'message': 'رمز عبور قبلی وارد شده اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save()
        return Response({'message': 'رمز عبور با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)
    

# forgot password
class ForgotPasswordViewset(APIView):
    permission_classes = [AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request):
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
        mobile = user.mobile
        expire = timezone.now() + timedelta(minutes=10)
        code_create, created = CodeForgotPassword.objects.update_or_create(user=user,defaults={'code': random.randint(100000, 999999),'expire': expire, 'status': False})
        serializer = CodeForgotPasswordSerializer(code_create).data
        code = serializer['code']

        notification_service = NotificationService()
        notification_service.send_sms(to = str(mobile), message=str(code), template='password_reset')

        if created:
            code_create.status = True
            code_create.save()
            return Response({'message': 'کد تایید ارسال شد'}, status=status.HTTP_200_OK)

        return Response({'message': 'کد تایید ارسال شد'}, status=status.HTTP_200_OK)


    def patch(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'message': 'کد تایید وارد نشده است'}, status=status.HTTP_400_BAD_REQUEST)
        
        code_obj = CodeForgotPassword.objects .filter(code=code,status=False, expire__gte=timezone.now()).first()

        if not code_obj:
            return Response({'message': 'کد تایید اشتباه است یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)
        user = code_obj.user
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        if not new_password or not new_password_confirm or new_password != new_password_confirm:
            return Response({'message': 'رمز عبور وارد شده با تکرار آن مطابقت ندارد'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save()
        
        code_obj.status = True
        code_obj.save()
        
        return Response({'message': 'رمز عبور با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)


# user profile
class ProfileViewset(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
       

        user_serializer = UserSerializer(user).data

        accounts = Accounts.objects.filter(user=user)
        accounts_serializer = AccountsSerializer(accounts, many=True).data

        addresses = Addresses.objects.filter(user=user)
        addresses_serializer = AddressesSerializer(addresses, many=True).data

        jobInfo = JobInfo.objects.filter(user=user).first()
        jobInfo_serializer = JobInfoSerializer(jobInfo, many=False).data

        if AgentUser.objects.filter(user=user) :
            agentUser = AgentUser.objects.filter(user=user).first()
            agentUser_serializer = AgentUserSerializer(agentUser, many=False).data
        else :
            agentUser_serializer = None

        if is_legal_person(user) == True :
            legal_person = LegalPerson.objects.filter(user=user).first()
            legal_person_serializer = LegalPersonSerializer(legal_person, many=False).data

            legal_person_shareholders = legalPersonShareholders.objects.filter(user=user)
            legal_person_shareholders_serializer = legalPersonShareholdersSerializer(legal_person_shareholders, many=True).data

            legal_person_stakeholders = legalPersonStakeholders.objects.filter(user=user)
            legal_person_stakeholders_serializer = legalPersonStakeholdersSerializer(legal_person_stakeholders, many=True).data
        else :
            legal_person_serializer = None
            legal_person_shareholders_serializer = None
            legal_person_stakeholders_serializer = None

        combined_data = {
            **user_serializer,
            'accounts' : accounts_serializer,
            'addresses' : addresses_serializer,
            'jobInfo' : jobInfo_serializer,
            'agentUser' : agentUser_serializer,
            'legal_person' : legal_person_serializer,
            'legal_person_shareholders' : legal_person_shareholders_serializer,
            'legal_person_stakeholders' : legal_person_stakeholders_serializer,
        }
        
        return Response( combined_data,status=status.HTTP_200_OK)


# all users for admin
class UserViewset(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        user = request.user
        user = User.objects.all()
        user_serializer = UserSerializer(user, many=True)
        print(user_serializer.data)
        return Response(user_serializer.data,status=status.HTTP_200_OK)
    

class UserDetailViewset(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user_serializer = UserSerializer(user).data

            accounts = Accounts.objects.filter(user=user)
            accounts_serializer = AccountsSerializer(accounts, many=True).data

            addresses = Addresses.objects.filter(user=user)
            addresses_serializer = AddressesSerializer(addresses, many=True).data

            jobInfo = JobInfo.objects.filter(user=user).first()
            jobInfo_serializer = JobInfoSerializer(jobInfo, many=False).data

            if AgentUser.objects.filter(user=user) :
                agentUser = AgentUser.objects.filter(user=user).first()
                agentUser_serializer = AgentUserSerializer(agentUser, many=False).data
            else :
                agentUser_serializer = None

            if is_legal_person(user) == True :
                legal_person = LegalPerson.objects.filter(user=user).first()
                legal_person_serializer = LegalPersonSerializer(legal_person, many=False).data

                legal_person_shareholders = legalPersonShareholders.objects.filter(user=user)
                legal_person_shareholders_serializer = legalPersonShareholdersSerializer(legal_person_shareholders, many=True).data

                legal_person_stakeholders = legalPersonStakeholders.objects.filter(user=user)
                legal_person_stakeholders_serializer = legalPersonStakeholdersSerializer(legal_person_stakeholders, many=True).data
            else :
                legal_person_serializer = None
                legal_person_shareholders_serializer = None
                legal_person_stakeholders_serializer = None

            combined_data = {
                **user_serializer,
                'accounts' : accounts_serializer,
                'addresses' : addresses_serializer,
                'jobInfo' : jobInfo_serializer,
                'agentUser' : agentUser_serializer,
                'legal_person' : legal_person_serializer,
                'legal_person_shareholders' : legal_person_shareholders_serializer,
                'legal_person_stakeholders' : legal_person_stakeholders_serializer,
            }
        
            return Response( combined_data,status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'message': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        

class SejamDataReceiverViewset(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        try:
            # دریافت داده‌ها از مونگو
            data = request.data
            uniqueIdentifier = data.get('uniqueIdentifier')
            if not uniqueIdentifier:
                return Response({'message': 'شناسه یکتا وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)

            # چک کردن وجود یوزر
            if User.objects.filter(uniqueIdentifier=uniqueIdentifier).exists():
                return Response({'message': 'کاربر قبلا ثبت شده است'}, status=status.HTTP_400_BAD_REQUEST)

            # ایجاد کاربر جدید
            private_person_data = data.get('privatePerson', {})
            new_user = User(
                username=uniqueIdentifier,
                email=data.get('email'),
                is_active=True,
                first_name=private_person_data.get('firstName'),
                last_name=private_person_data.get('lastName'),
                mobile=data.get('mobile'),
                gender='M' if private_person_data.get('gender') == 'Male' else 'F' if private_person_data.get('gender') == 'Female' else None,
                birth_date=parse_date(private_person_data.get('birthDate')),
                created_at=parse_date(data.get('createdAt')),
                updated_at=parse_date(data.get('updatedAt')),
                address=data['addresses'][0].get('remnantAddress') if data.get('addresses') and len(data['addresses']) > 0 else None,
                status=True if data.get('status') == 'Sejami' else False,
                uniqueIdentifier=uniqueIdentifier,
                seri_shenasname=private_person_data.get('seriSh'),
                seri_shenasname_char=private_person_data.get('seriShChar'),
                serial_shenasname=private_person_data.get('serial'),
                place_of_birth=private_person_data.get('placeOfBirth'),
                place_of_issue=private_person_data.get('placeOfIssue'),
                father_name=private_person_data.get('fatherName'),
                is_sejam_registered=data.get('is_sejam_registered',True),
            )
            new_user.set_password(uniqueIdentifier)
            new_user.save()
            if data.get('is_sejam_registered') == False:
                return Response({'message': 'کاربر با موفقیت ثبت شد'}, status=status.HTTP_200_OK)

            # ذخیره اطلاعات سهامداران حقوقی
            if data.get('legalPersonStakeholders'):
                for stakeholder_data in data['legalPersonStakeholders']:
                    new_stakeholder = legalPersonStakeholders(
                        user=new_user,
                        uniqueIdentifier=stakeholder_data['uniqueIdentifier'],
                        type=stakeholder_data['type'],
                        start_at=stakeholder_data['startAt'],
                        position_type=stakeholder_data['positionType'],
                        last_name=stakeholder_data['lastName'],
                        is_owner_signature=stakeholder_data['isOwnerSignature'],
                        first_name=stakeholder_data['firstName'],
                        end_at=stakeholder_data['endAt']
                    )
                    new_stakeholder.save()

            # ذخیره اطلاعات شخص حقوقی
            if data.get('legalPerson'):
                legal_person_data = data['legalPerson']
                new_legal_person = LegalPerson(
                    user=new_user,
                    company_name=legal_person_data['companyName'],
                    citizenship_country=legal_person_data['citizenshipCountry'],
                    economic_code=legal_person_data['economicCode'],
                    evidence_expiration_date=legal_person_data['evidenceExpirationDate'],
                    evidence_release_company=legal_person_data['evidenceReleaseCompany'],
                    evidence_release_date=legal_person_data['evidenceReleaseDate'],
                    legal_person_type_sub_category=legal_person_data['legalPersonTypeSubCategory'],
                    register_date=legal_person_data['registerDate'],
                    legal_person_type_category=legal_person_data['legalPersonTypeCategory'],
                    register_place=legal_person_data['registerPlace'],
                    register_number=legal_person_data['registerNumber']
                )
                new_legal_person.save()

            # ذخیره اطلاعات سهامداران
            if data.get('legalPersonShareholders'):
                for shareholder_data in data['legalPersonShareholders']:
                    new_shareholder = legalPersonShareholders(
                        user=new_user,
                        uniqueIdentifier=shareholder_data['uniqueIdentifier'],
                        postal_code=shareholder_data['postalCode'],
                        position_type=shareholder_data['positionType'],
                        percentage_voting_right=shareholder_data['percentageVotingRight'],
                        first_name=shareholder_data['firstName'],
                        last_name=shareholder_data['lastName'],
                        address=shareholder_data['address']
                    )
                    new_shareholder.save()

            # ذخیره اطلاعات حساب‌های بانکی
            if data.get('accounts'):
                for account_data in data['accounts']:
                    new_account = Accounts(
                        user=new_user,
                        account_number=account_data['accountNumber'],
                        bank=account_data['bank']['name'],
                        branch_code=account_data['branchCode'],
                        branch_name=account_data['branchName'],
                        is_default=account_data['isDefault'],
                        type=account_data['type'],
                        sheba_number=account_data['sheba']
                    )
                    new_account.save()

            # ذخیره اطلاعات آدرس‌ها
            if data.get('addresses'):
                for address_data in data['addresses']:
                    new_address = Addresses(
                        user=new_user,
                        alley=address_data['alley'],
                        city=address_data['city']['name'],
                        city_prefix=address_data['cityPrefix'],
                        country=address_data['country']['name'],
                        country_prefix=address_data['countryPrefix'],
                        email=address_data['email'],
                        emergency_tel=address_data['emergencyTel'],
                        emergency_tel_city_prefix=address_data['emergencyTelCityPrefix'],
                        emergency_tel_country_prefix=address_data['emergencyTelCountryPrefix'],
                        fax=address_data['fax'],
                        fax_prefix=address_data['faxPrefix'],
                        plaque=address_data['plaque'],
                        postal_code=address_data['postalCode'],
                        province=address_data['province']['name'],
                        remnant_address=address_data['remnantAddress'],
                        section=address_data['section']['name'],
                        tel=address_data['tel']
                    )
                    new_address.save()

            # ذخیره اطلاعات شغلی
            if data.get('jobInfo'):
                job_data = data['jobInfo']
                new_job = JobInfo(
                    user=new_user,
                    company_address=job_data.get('companyAddress'),
                    company_city_prefix=job_data.get('companyCityPrefix'),
                    company_email=job_data.get('companyEmail'),
                    company_fax=job_data.get('companyFax'),
                    company_fax_prefix=job_data.get('companyFaxPrefix'),
                    company_name=job_data.get('companyName'),
                    company_phone=job_data.get('companyPhone'),
                    company_postal_code=job_data.get('companyPostalCode'),
                    company_web_site=job_data.get('companyWebSite'),
                    employment_date=job_data.get('employmentDate'),
                    job_title=job_data.get('job', {}).get('title'),
                    job_description=job_data.get('jobDescription'),
                    position=job_data.get('position')
                )
                new_job.save()

            # ذخیره اطلاعات نماینده
            if data.get('agent'):
                agent_data = data['agent']
                new_agent = AgentUser(
                    user=new_user,
                    description=agent_data.get('description'),
                    expiration_date=agent_data.get('expirationDate'),
                    first_name=agent_data.get('firstName'),
                    is_confirmed=agent_data.get('isConfirmed'),
                    last_name=agent_data.get('lastName'),
                    type=agent_data.get('type'),
                    father_uniqueIdentifier=agent_data.get('uniqueIdentifier')
                )
                new_agent.save()

            return Response({
                'message': 'داده‌های سجام با موفقیت پردازش شدند'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'message': f'خطا در پردازش داده‌های سجام: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateProfileImageViewset(APIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def patch(self, request):
        user = request.user
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')
            print(user.profile_image)
            user.save()
        user_serializer = UserSerializer(user).data
        return Response(user_serializer, status=status.HTTP_200_OK)
