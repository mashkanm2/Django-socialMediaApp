import random
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.timezone import now
from django.conf import settings
from django.core.validators import MinLengthValidator
from .validators import number_validator, special_char_validator, letter_validator
from config.tasks import send_OtpRegisterCode_task
from djagosocialmediaapp.users.models import BaseUser,OtpCode
from djagosocialmediaapp.api.mixins import ApiAuthMixin
from djagosocialmediaapp.users.selectors import get_profile
from djagosocialmediaapp.users.services import register 
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from drf_spectacular.utils import extend_schema



class RegisterApi(APIView):
    class InputRegisterSerializer(serializers.Serializer):
        user_name=serializers.CharField(max_length=100,required=True)
        email = serializers.EmailField(max_length=255,required=True)
        phone_number=serializers.CharField(max_length=11,required=True)
        password = serializers.CharField(validators=[
                        number_validator,
                        MinLengthValidator(limit_value=4)
                    ]
                )
        

        def validate(self, data):
            ### Validation if user exist
            user_nm=data.get('user_name')
            email_=data.get('email')
            phone_number_=data.get('phone_number')
            if user_nm and email_ and phone_number_:
                # Check if user_name,email and phone_number exists
                ret_exist=BaseUser.objects.filter(Q(user_name=user_nm) |
                                    Q(email=email_) |
                                    Q(phone_number=phone_number_)).exists()
                if ret_exist:
                    raise serializers.ValidationError('user_name | email | phone_number  already exists')
            
            return data
    
    class OutPutRegisterSerializer(serializers.Serializer):
        user_name=serializers.CharField(max_length=100)
        email = serializers.EmailField(max_length=255)
        phone_number=serializers.CharField(max_length=11)
    
    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user=BaseUser.objects.create_user(user_name=serializer.validated_data.get("user_name"),
                                         email=serializer.validated_data.get("email"),
                                         email=serializer.validated_data.get("phone_number"),
                                         password=serializer.validated_data.get("password"),
                                         activate=False)
            ### create otp Code
            random_code=random.randint(1000,9999)
            ## TODO : convert to celery task
            send_OtpRegisterCode_task(serializer.validated_data.get("phone_number"),random_code)
            # send_otp_code.apply_async(args=[serializer.validated_data.get("phone_number"),random_code])
            OtpCode.objects.create(phone_number=serializer.validated_data.get("phone_number"),code=random_code)
            
        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        out_res=self.OutPutRegisterSerializer(data={
            "user_name":serializer.validated_data.get("user_name"),
            "email":serializer.validated_data.get("email"),
            "phone_number":serializer.validated_data.get("phone_number"),
            },
            context={"request":request})
        # return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data)
        return Response(out_res.data)





class UserRegisterVerifyOtpCodeView(APIView):

    class InputVerifyOtpCodeSerializer(serializers.Serializer):
        user_name=serializers.CharField(max_length=100)
        email = serializers.EmailField(max_length=255)
        phone_number=serializers.CharField(max_length=11)  

    class OutputVerifyOtpCodeSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = ("user_name","email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data


    @extend_schema(request=InputVerifyOtpCodeSerializer, responses=OutputVerifyOtpCodeSerializer)
    def post(self, request):
        serializer = self.InputVerifyOtpCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_name=serializer.validated_data.get("user_name")
            email = serializer.validated_data.get("email")
            phone_number=serializer.validated_data("phone_number")
            if user_name and email and phone_number:
                user_query = BaseUser.objects.filter(user_name=user_name,email=email,phone_number=phone_number)
                user=get_object_or_404(user_query)

                code_query=OtpCode.objects.get(phone_number=phone_number)
                code_instance=get_object_or_404(code_query)

                if code_instance.code != serializer.validated_data.get("otp_code"):
                    return Response(
                        f"Invalid Code {ex}",
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # DONE : check "code" timeDate expired
                cu_datetime_utc=now()
                code_time_spended=(cu_datetime_utc-code_instance.created).total_seconds()
                if code_time_spended>settings.EXPIRED_TIME_OTPCODE_SECEND:
                    return Response(
                        f"Expired Code {ex}",
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # activate user and delete otp code
                user.is_active=True
                user.save()
                code_instance.delete()  # ==> TODO: create job schuler to delete old codes


        except Http404 as ef:
            return Response(
                    f"Invalid Data {ex}",
                    status=status.HTTP_404_NOT_FOUND
                    )

        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(self.OutputVerifyOtpCodeSerializer(user, context={"request":request}).data)

