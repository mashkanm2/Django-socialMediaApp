import random
import datetime
from django.db import transaction 
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.conf import settings
from .models import BaseUser, OtpCode,UserProfile
from .tasks import send_OtpRegisterCode_task

def create_profile(*, user:BaseUser) -> UserProfile:
    return UserProfile.objects.create(user=user)

def create_user(*, user_name:str,email:str,phone_number:str, password:str) -> BaseUser:
    # return BaseUser.objects.create_user(email=email, password=password)

    user=BaseUser.objects.create_user(user_name=user_name,
                                    email=email,
                                    phone_number=phone_number,
                                    password=password,
                                    activate=False)
    ### create otp Code
    random_code=random.randint(1000,9999)
    ## TODO : convert to celery task
    send_OtpRegisterCode_task(phone_number,random_code)
    # send_otp_code.apply_async(args=[serializer.validated_data.get("phone_number"),random_code])
    OtpCode.objects.create(phone_number=phone_number,code=random_code)
    return user

def activate_user_verifyCode(*,user_name,email:str,phone_number:str,otp_code:int) -> str:
    
    err_msg=None

    user_query = BaseUser.objects.filter(user_name=user_name,email=email,phone_number=phone_number)
    user=get_object_or_404(user_query)

    code_query=OtpCode.objects.filter(phone_number=phone_number)
    code_instance=get_object_or_404(code_query)

    if code_instance.code != otp_code:
        err_msg="Invalid Code."


    # DONE : check "code" timeDate expired
    cu_datetime_utc=now()
    code_time_spended=(cu_datetime_utc-code_instance.created).total_seconds()
    if code_time_spended>settings.EXPIRED_TIME_OTPCODE_SECEND:
        err_msg="Expired Code."

    # activate user and delete otp code
    user.is_active=True
    user.save()
    code_instance.delete()  # ==> TODO: create job schuler to delete old codes

    return user,err_msg

@transaction.atomic
def register(*, user_name:str,email:str,phone_number:str, password:str) -> BaseUser:

    user = create_user(user_name=user_name,email=email,phone_number=phone_number,password=password)
    create_profile(user=user)

    return user


def update_profile(*,user:BaseUser,first_name:str |None,last_name:str|None,
                   date_of_birth:datetime.datetime|None,
                   profile_picture:str|None,city_address:str|None) -> UserProfile:
    
    user_profile = get_object_or_404(UserProfile, user=user)
    user_profile.first_name = first_name
    user_profile.last_name = last_name
    user_profile.date_of_birth = date_of_birth
    user_profile.profile_picture=profile_picture
    user_profile.city_address=city_address
    user_profile.save()
    return user_profile
