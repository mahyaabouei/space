from user.models import LegalPerson , legalPersonShareholders , legalPersonStakeholders



# جک کاربر حقوقیه
def is_legal_person(user):
    legal_person = LegalPerson.objects.filter(user=user).first()
    if legal_person :
        return True
    return False
