# from time import sleep
# from celery import shared_task

import datetime
from tripplanapp.users.models import OtpCode

def clear_expired_OTPcodes():
    OtpCode.objects.filter(expiry_date__lt=datetime.datetime.now(...)).delete()

# @shared_task()
def send_OtpRegisterCode_task(phone_number,code):
    pass
