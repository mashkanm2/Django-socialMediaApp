# from time import sleep
# from celery import shared_task



# @shared_task
# def notify_customers(message):
#     print(message)
#     sleep(10)

import datetime
from djagosocialmediaapp.users.models import OtpCode

def clear_expired_OTPcodes():
    OtpCode.objects.filter(expiry_date__lt=datetime.datetime.now(...)).delete()

# @shared_task()
def send_OtpRegisterCode_task(phone_number,code):
    pass
