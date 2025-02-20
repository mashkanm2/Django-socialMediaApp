import datetime

from accounts.models import OtpCode

def clear_expired_OTPcodes():
    OtpCode.objects.filter(expiry_date__lt=datetime.datetime.now(...)).delete()
