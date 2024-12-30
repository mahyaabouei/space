from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
class Gender(models.TextChoices):
    MALE = 'M', 'مرد'
    FEMALE = 'F', 'زن'
    OTHER = 'O', 'دیگر'


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True , null=True , blank=True)
    password = models.TextField()
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255,null=True , blank=True)
    last_name = models.CharField(max_length=255,null=True , blank=True)
    mobile = models.CharField(max_length=13)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.OTHER)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(null=True , blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True) 
    last_login = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True)
    uniqueIdentifier = models.CharField(max_length=20)
    chat_id_telegram = models.CharField(max_length=255, null=True, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0) 
    seri_shenasname = models.CharField(max_length=15, null=True, blank=True)
    seri_shenasname_char = models.CharField(max_length=15, null=True, blank=True)
    serial_shenasname = models.CharField(max_length=15, null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, null=True, blank=True)
    place_of_issue = models.CharField(max_length=255, null=True, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    is_sejam_registered = models.BooleanField(default=True)

    EDUCATION_LEVELS = [
    ('highschool', 'دیپلم'),
    ('bachelor', 'کارشناسی'),
    ('master', 'کارشناسی ارشد'),
    ('phd', 'دکترا'),
    ]
    education_level = models.CharField(max_length=15, choices=EDUCATION_LEVELS, blank=True, null=True) 
    MARITAL_STATUS = [
    ('single', 'مجرد'),
    ('married', 'متاهل'),
    ]
    marital_status = models.CharField(max_length=15, choices=MARITAL_STATUS, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
    )

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Accounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20 ,null=True , blank=True)
    bank = models.CharField(max_length=255,null=True , blank=True)
    branch_code = models.CharField(max_length=120 ,null=True , blank=True)
    branch_name = models.CharField(max_length=255 , null=True , blank=True)
    is_default = models.BooleanField(default=False)
    sheba_number = models.CharField(max_length=35 , null=True , blank=True)
    type = models.CharField(max_length=150, null=True, blank=True)


    def __str__(self):
        return self.user.username


class Addresses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    country = models.CharField(max_length=100, verbose_name='کشور' , null=True , blank=True)
    country_prefix = models.CharField(max_length=25, verbose_name='پیش شماره کشور', null=True, blank=True)
    province = models.CharField(max_length=100, verbose_name='استان' , null=True , blank=True)
    city = models.CharField(max_length=100, verbose_name='شهر' , null=True , blank=True)
    city_prefix = models.CharField(max_length=15, verbose_name='پیش شماره شهر', null=True, blank=True)
    section = models.CharField(max_length=100, verbose_name='بخش' , null=True , blank=True)
    remnant_address = models.TextField(verbose_name='ادامه آدرس' , null=True , blank=True)
    alley = models.CharField(max_length=100, verbose_name='کوچه', null=True, blank=True)
    plaque = models.CharField(max_length=15, verbose_name='پلاک' , null=True, blank=True)
    postal_code = models.CharField(max_length=15, verbose_name='کد پستی' ,null=True , blank=True)
    tel = models.CharField(max_length=20, verbose_name='تلفن ثابت', null=True, blank=True)
    emergency_tel = models.CharField(max_length=20, verbose_name='تلفن اضطراری', null=True, blank=True)
    emergency_tel_city_prefix = models.CharField(max_length=20, verbose_name='پیش شماره شهر تلفن اضطراری', null=True, blank=True)
    emergency_tel_country_prefix = models.CharField(max_length=15, verbose_name='پیش شماره کشور تلفن اضطراری', null=True, blank=True)
    fax = models.CharField(max_length=20, verbose_name='فکس', null=True, blank=True)
    fax_prefix = models.CharField(max_length=15, verbose_name='پیش شماره فکس', null=True, blank=True)
    email = models.EmailField(verbose_name='ایمیل', null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.city}"


class JobInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_infos')
    company_name = models.CharField(max_length=255, verbose_name='نام شرکت', null=True, blank=True)
    company_address = models.TextField(verbose_name='آدرس شرکت', null=True, blank=True)
    company_city_prefix = models.CharField(max_length=15, verbose_name='پیش شماره شهر شرکت', null=True, blank=True)
    company_phone = models.CharField(max_length=20, verbose_name='تلفن شرکت', null=True, blank=True)
    company_postal_code = models.CharField(max_length=15, verbose_name='کد پستی شرکت', null=True, blank=True)
    company_email = models.EmailField(verbose_name='ایمیل شرکت', null=True, blank=True)
    company_fax = models.CharField(max_length=20, verbose_name='فکس شرکت', null=True, blank=True)
    company_fax_prefix = models.CharField(max_length=15, verbose_name='پیش شماره فکس شرکت', null=True, blank=True)    
    job_title = models.CharField(max_length=255, verbose_name='عنوان شغل', null=True, blank=True)
    position = models.CharField(max_length=255, verbose_name='سمت', null=True, blank=True)
    job_description = models.TextField(verbose_name='شرح شغل', null=True, blank=True)
    company_web_site = models.TextField(verbose_name='ادرس شرکت', null=True, blank=True)
    employment_date = models.DateField(verbose_name='تاریخ استخدام', null=True, blank=True)
    is_current = models.BooleanField(default=True, verbose_name='شغل فعلی')

    class Meta:
        verbose_name = 'اطلاعات شغلی'
        verbose_name_plural = 'اطلاعات شغلی'

    def __str__(self):
        return f"{self.user.username} - {self.job_title or 'بدون عنوان شغلی'}"



class Otp(models.Model):
    code = models.CharField(max_length=6)
    mobile = models.CharField(max_length=14)


    def __str__(self):
        return f"{self.mobile} - {self.code}"


class AgentUser (models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    expiration_date = models.CharField(max_length=150, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    is_confirmed = models.BooleanField( default= True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    type = models.CharField(max_length=150, null=True, blank=True)
    father_uniqueIdentifier = models.CharField(max_length=150, null=True, blank=True)


class LegalPerson (models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    citizenship_country = models.CharField( max_length=150 , null=True , blank= True)
    company_name = models.CharField( max_length=150 , null=True , blank= True)
    economic_code = models.CharField( max_length=150 , null=True , blank= True)
    evidence_expiration_date = models.CharField( max_length=150 , null=True , blank= True)
    evidence_release_company = models.CharField( max_length=150 , null=True , blank= True)
    evidence_release_date = models.CharField( max_length=150 , null=True , blank= True)
    legal_person_type_sub_category = models.CharField( max_length=150 , null=True , blank= True)
    register_date = models.CharField( max_length=150 , null=True , blank= True)
    legal_person_type_category = models.CharField( max_length=150 , null=True , blank= True)
    register_place = models.CharField( max_length=150 , null=True , blank= True)
    register_number = models.CharField( max_length=150 , null=True , blank= True)


class legalPersonShareholders (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniqueIdentifier = models.CharField( max_length=20 , null=True , blank= True)
    postal_code = models.CharField( max_length=20 , null=True , blank= True)
    position_type = models.CharField( max_length=50 , null=True , blank= True)
    percentage_voting_right = models.CharField( max_length=50 , null=True , blank= True)
    last_name = models.CharField( max_length=50 , null=True , blank= True)
    first_name = models.CharField( max_length=50 , null=True , blank= True)
    address = models.TextField( max_length=150 , null=True , blank= True)
    


class legalPersonStakeholders (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uniqueIdentifier = models.CharField( max_length=150 , null=True , blank= True)
    type = models.CharField( max_length=150 , null=True , blank= True)
    start_at = models.CharField( max_length=150 , null=True , blank= True)
    position_type = models.CharField( max_length=150 , null=True , blank= True)
    last_name = models.CharField( max_length=150 , null=True , blank= True)
    is_owner_signature = models.CharField( max_length=150 , null=True , blank= True)
    first_name = models.CharField( max_length=150 , null=True , blank= True)
    end_at = models.CharField( max_length=150 , null=True , blank= True)



class UUid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    status = models.BooleanField(default=True)
    expire = models.DateTimeField(null=True, blank=True)   



class CodeForgotPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expire = models.DateTimeField()
    status = models.BooleanField(default=False)



