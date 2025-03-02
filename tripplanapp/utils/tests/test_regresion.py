
import datetime
from django.test import TestCase,Client
from django.urls import reverse
from unittest import mock

from tripplanapp.users.models import BaseUser,OtpCode,UserProfile


class Test_UserModelRegister(TestCase):
    def setUp(self):
        self.client = Client()
        return super().setUp()
    
    @classmethod
    def setUpTestData(cls):
        
        user=BaseUser.objects.create_user(user_name='user3',email='user3@email.com',
                                     phone_number='09137654321',password='2345')
        
        UserProfile.objects.create(user=user)

        return super().setUpTestData()
    

    def test_userRegister_With_OtpCode(self):
        response = self.client.post(reverse('api:users:register'),
                                    data={'user_name':'user4','email':'user4@email.com',
                                          'phone_number':'09141234567','password':'567888888'},
                                    content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['user_name'],'user4')
        self.assertEqual(response.json()['email'],'user4@email.com')
        self.assertEqual(response.json()['phone_number'],'09141234567')

        ### get otp code
        otp_code = OtpCode.objects.get(phone_number='09141234567')
        response2=self.client.post(reverse('api:users:vrifycode'),
                                    data={'user_name':'user4','email':'user4@email.com',
                                         'phone_number':'09141234567','otp_code':otp_code.code},
                                    content_type='application/json')
        
        
        self.assertEqual(response2.status_code,200)
        self.assertEqual(response2.json()['user_name'],'user4')
        self.assertEqual(response2.json()['email'],'user4@email.com')
        self.assertIsNotNone(response2.json()['token'].get('refresh'))
        self.assertIsNotNone(response2.json()['token'].get('access'))

        ## check deleted code
        self.assertEqual(OtpCode.objects.count(),0)

    @mock.patch('tripplanapp.users.services.now')
    def test_verifyOtpCode_expired(self,mock_now):
        mock_now.side_effect=[datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(days=1)]

        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09127654321','password':'1234567'}
        response=self.client.post(reverse('api:users:register'),data=data_)

        code_=OtpCode.objects.last().code
        response=self.client.post(reverse('api:users:vrifycode'),
                                  data={'user_name':'user4','email':'user4@email.com',
                                         'phone_number':'09127654321','otp_code':code_})
        self.assertEqual(response.status_code,400)

        user4=BaseUser.objects.get(user_name="user4")
        self.assertFalse(user4.is_active)


    def test_login_notActivatedUser(self):
        data_={'user_name':'user4','email':'user4@email.com','phone_number':'09126664321','password':'1234567'}
        response=self.client.post(reverse('api:users:register'),data=data_)
        self.assertEqual(response.status_code,200)
        self.assertFalse(BaseUser.objects.get(user_name="user4").is_active)
        data_2={"user_name":"user4","password":"1234567"}
        response=self.client.post(reverse('api:users:jwt:login'),data=data_2)
        print(response)
        self.assertEqual(response.status_code,403)