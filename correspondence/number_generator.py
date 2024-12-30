from django.utils import timezone
from correspondence.models import Number , Correspondence
from persiantools.jdatetime import JalaliDate
from companies.models import Company


class CorrespondenceNumberGenerator:
    @staticmethod
    def generate_number():
        """
        تولید شماره نامه جدید
        مثال: 1400/1234567890/0001
        """
        year = JalaliDate.today().year
        last_correspondence_number = Number.objects.filter(jalali_year=year).order_by('-number').first()
        if last_correspondence_number:
            new_sequence = last_correspondence_number.number + 1
        else:
            new_sequence = 10001
        
        number_obj = Number.objects.create(number=new_sequence, jalali_year=year)
        company_registration = Company.objects.first().registration_number
        new_number = f"{year}/{company_registration}/{new_sequence}"
        return new_number , number_obj