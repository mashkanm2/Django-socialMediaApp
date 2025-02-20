from django.test import TestCase,Client
from django.urls import reverse
from unittest import mock
import datetime
from .models import User,OtpCode
from .forms import UserRegisterFormAdmin,UserChangeForm,UserRegistrationForm,VerifyCodeForm


class Test_UserModelRegister(TestCase):
    def setUp(self):
        self.client=Client()
        # self.cu_dateTime=datetime.datetime.now(tz=datetime.timezone.utc)
        return super().setUp()
    
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(user_name='user3',email='user3@email.com',phone_number='09137654321',password='edcrfv')

        return super().setUpTestData()
    
    
    def test_valid_data(self):
        form=UserRegisterFormAdmin(data={'user_name':'user5',
                                         'email':'user5@email.com',
                                         'phone_number':'09157654321',
                                         'first_name':'k','last_name':'ke',
                                         'password1':'1234567',
                                         'password2':'1234567'})
        self.assertTrue(form.is_valid())
    
    def test_valid_data_none(self):
        form=UserRegisterFormAdmin(data={'user_name':'user5',
                                         'email':'user5@email.com',
                                         'phone_number':'09157654321',
                                         'first_name':None,'last_name':None,
                                         'password1':'1234567',
                                         'password2':'1234567'})
        
        self.assertTrue(form.is_valid())

    def test_valid_data_password_none(self):
        form=UserRegisterFormAdmin(data={'user_name':'user3',
                                         'email':'user3@email.com',
                                         'phone_number':'09127654321',
                                         'password1':None,
                                         'password2':None})
        self.assertFalse(form.is_valid())
    #########################################################

    def test_empty_data(self):
        form=UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors),4)

    def test_exist_username(self):
        form=UserRegistrationForm(data={'user_name':'user3',
                                         'email':'user4@email.com',
                                         'phone_number':'09127654321',
                                         'password':'1234567'})
        self.assertEqual(len(form.errors),1)

    def test_exist_email(self):
        # User.objects.create_user(user_name='user3',email='user3@email.com',phone_number='09137654321',password='edcrfv')
        form=UserRegistrationForm(data={'user_name':'user4',
                                         'email':'user3@email.com',
                                         'phone_number':'09127654321',
                                         'password':'1234567'})
        self.assertEqual(len(form.errors),1)
    def test_exist_phone_number(self):
        # User.objects.create_user(user_name='user3',email='user3@email.com',phone_number='09137654321',password='edcrfv')
        form=UserRegistrationForm(data={'user_name':'user4',
                                         'email':'user4@email.com',
                                         'phone_number':'09137654321',
                                         'password':'1234567'})
        self.assertEqual(len(form.errors),1)

    #########################################################
    def test_user_model_register_GET(self):
        response=self.client.get(reverse('accounts:sign_up'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/register.html')
        self.assertEqual(response.context['form'],UserRegistrationForm)

    def test_user_model_register_POST(self):
        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09127654321','password':'1234567'}
        response=self.client.post(reverse('accounts:sign_up'),data=data_)
        self.assertEqual(self.client.session['user_registration_info'],data_)
        self.assertEqual(response.status_code,302) ## 302 : redirect
        self.assertRedirects(response,reverse('accounts:verify_code'))
    

    def test_otpcode_correct(self):
        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09127654321','password':'1234567'}
        response=self.client.post(reverse('accounts:sign_up'),data=data_)

        code_=OtpCode.objects.last().code
        response=self.client.post(reverse('accounts:verify_code'),data={'code':code_})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse('Home:home'))
        self.assertEqual(User.objects.count(),2)

    def test_otpcode_incorrect(self):
        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09127654321','password':'1234567'}
        response=self.client.post(reverse('accounts:sign_up'),data=data_)

        response=self.client.post(reverse('accounts:verify_code'),data={'code':123})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse('accounts:verify_code'))
        self.assertEqual(User.objects.count(),1)

    @mock.patch('accounts.views.now')
    def test_otpcode_expiration(self,mock_now):
        mock_now.side_effect=[datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(days=1)]
        
        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09127654321','password':'1234567'}
        response=self.client.post(reverse('accounts:sign_up'),data=data_)

        code_=OtpCode.objects.last().code
        response=self.client.post(reverse('accounts:verify_code'),data={'code':code_})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/verify.html')
        self.assertEqual(User.objects.count(),1)

        messages_ = list(response.context['messages'])
        self.assertTrue(len(messages_)>0)
        self.assertEqual(str(messages_[-1]), 'code expired')
