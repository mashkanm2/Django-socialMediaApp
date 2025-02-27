
from rest_framework import status,generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework import serializers
from django.db.models import Q
from django.http import Http404

from django.core.validators import MinLengthValidator
from tripplanapp.users.models import BaseUser,UserProfile
from tripplanapp.api.mixins import ApiAuthMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from drf_spectacular.utils import extend_schema,OpenApiResponse
from .validators import number_validator, special_char_validator, letter_validator
from .services import register,activate_user_verifyCode


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
            user_name_=serializer.validated_data.get("user_name")
            email_=serializer.validated_data.get("email")
            phone_number_=serializer.validated_data.get("phone_number")
            password_=serializer.validated_data.get("password")
            user=register(user_name=user_name_,email=email_,phone_number=phone_number_, password=password_)
            
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
        out_res.is_valid(raise_exception=False)
        # return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data)
        return Response(out_res.data)





class UserRegisterVerifyOtpCodeView(APIView):

    class InputVerifyOtpCodeSerializer(serializers.Serializer):
        user_name=serializers.CharField(max_length=100)
        email = serializers.EmailField(max_length=255)
        phone_number=serializers.CharField(max_length=11)
        otp_code=serializers.IntegerField()

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
        
    

    @extend_schema(request=InputVerifyOtpCodeSerializer,
                   responses={
                       201: OpenApiResponse(response=OutputVerifyOtpCodeSerializer),
                       400:OpenApiResponse(),
                        },
                   )
    def post(self, request):
        serializer = self.InputVerifyOtpCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            
            user_name=serializer.validated_data.get("user_name")
            email = serializer.validated_data.get("email")
            phone_number=serializer.validated_data.get("phone_number")
            otp_code=serializer.validated_data.get("otp_code")
            if user_name and email and phone_number:
                user,err_msg=activate_user_verifyCode(user_name=user_name,email=email,
                                            phone_number=phone_number,otp_code=otp_code)
            else:
                return Response("Invalid Input Data.",status=status.HTTP_400_BAD_REQUEST)
            
            if err_msg and err_msg=="Invalid Code.":
                return Response("Invalid Code.",status=status.HTTP_400_BAD_REQUEST)
        
            if err_msg and err_msg=="Expired Code.":
                return Response("Expired Code.",status=status.HTTP_400_BAD_REQUEST)
        except Http404 as ef:
            return Response(
                    f"Invalid Data {ef}",
                    status=status.HTTP_400_BAD_REQUEST
                    )

        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(self.OutputVerifyOtpCodeSerializer(user, context={"request":request}).data)


# class UserProfileAPI(APIView):
#     class InputProfileSerializer(serializers.Serializer):
#         first_name = serializers.CharField(max_length=100, required=False)
#         last_name = serializers.CharField(max_length=100, required=False)
#         date_of_birth=serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'],required=False)
#         profile_picture=serializers.CharField(max_length=None,required=False)
#         city_address=serializers.CharField(max_length=None,required=False)

    
#     def 



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ['user','created_at','updated_at']
        
        

class ProfileUpdateView(generics.RetrieveUpdateAPIView,ApiAuthMixin):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=ProfileSerializer)
    def get_object(self):
        return Response(ProfileSerializer(self.request.user.profile).data)

