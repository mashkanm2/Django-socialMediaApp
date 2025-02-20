import random
from django.utils.timezone import now
from django.shortcuts import render,redirect
from django.views import View
from django.conf import settings
from django.contrib import messages

from .forms import UserRegistrationForm,VerifyCodeForm
from utils import send_otp_code
from .models import OtpCode,User


class UserRegisterView(View):
    form_class=UserRegistrationForm

    def get(self,request):
        form=self.form_class
        return render(request,'accounts/register.html',{'form':form})
        

    def post(self,request):
        '''
        extract user data from request and call send_otp_cod() 
        save user data on session and save random otp code on Db
        redirect to otp verification page
        '''
        form=self.form_class(request.POST)
        if form.is_valid():

            random_code=random.randint(1000,9999)
            send_otp_code(form.cleaned_data["phone_number"],random_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'],code=random_code)

            request.session["user_registration_info"]=form.cleaned_data

            messages.success(request,'we sent you a code','success')
            return redirect('accounts:verify_code')
        return render(request,'accounts/register.html',{'form':form})

class UserRegisterVerifyCodeView(View):

    form_class=VerifyCodeForm
    def get(self,request):
        form=self.form_class
        return render(request,'accounts/verify.html',{'form':form})

    def post(self,request):
        user_session_data=request.session['user_registration_info']
        form=self.form_class(request.POST)
        if form.is_valid():
            code_instance=OtpCode.objects.get(phone_number=user_session_data['phone_number'])
            if form.cleaned_data['code'] == code_instance.code:
                
                # DONE : check "code" timeDate expired
                cu_datetime_utc=now()
                code_time_spended=(cu_datetime_utc-code_instance.created).total_seconds()
                if code_time_spended>settings.EXPIRED_TIME_OTPCODE_SECEND:
                    messages.error(request, 'code expired', 'error')
                    return render(request,'accounts/verify.html',{'form':form})
                
                # create user and delete otp code
                User.objects.create_user(**user_session_data)
                code_instance.delete()  # ==> TODO: create job schuler to delete old codes
                messages.success(request,'you are registered successfully','success')
                return redirect('Home:home')
            else:
                messages.error(request,'invalid code','error')
                return redirect('accounts:verify_code')
        return redirect("Home:home")
