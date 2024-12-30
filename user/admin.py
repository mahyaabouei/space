from django.contrib import admin
from .models import User , Otp , Accounts , Addresses , JobInfo , LegalPerson , legalPersonShareholders , legalPersonStakeholders , UUid,AgentUser , CodeForgotPassword

    
admin.site.register(User)
admin.site.register(Otp)
admin.site.register(Accounts)
admin.site.register(Addresses)
admin.site.register(LegalPerson)
admin.site.register(legalPersonShareholders)
admin.site.register(legalPersonStakeholders)
admin.site.register(JobInfo)
admin.site.register(AgentUser)
admin.site.register(UUid)
admin.site.register(CodeForgotPassword)


