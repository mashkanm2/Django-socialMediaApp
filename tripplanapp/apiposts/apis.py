

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter
from django.core.cache import cache
from tripplanapp.api.mixins import ApiAuthMixin
from PIL import Image
from .selectors import get_user_post
from .services import upload_image_file

class FileFieldSerializer(serializers.Serializer):
    image=serializers.FileField(required=True)

## upload image on view -> return image url after upload
class ImageUploadView(APIView,ApiAuthMixin):
    @extend_schema(request=FileFieldSerializer,responses=Response)
    def post(self, request:Request):
        serializer = FileFieldSerializer(data=request.data)
        user=request.user
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            image = Image.open(image_file)
            task_id = upload_image_file(user_id=user.id,image_name=image_file.name,image=image)
            return Response({'message': 'Image received.'}, status=status.HTTP_202_ACCEPTED)
        
        return Response({'Image File not accepted.'}, status=status.HTTP_400_BAD_REQUEST)

class PostUploadView(APIView,ApiAuthMixin):
    class InputPostUploadSerializer(serializers.Serializer):
        title=serializers.CharField()
        location_name=serializers.CharField()
        categories=serializers.CharField(max_length=1000,required=False)
        
        def validate(self, attrs):
            return super().validate(attrs)
    class OutputPostUploadSerializer(serializers.Serializer):
        pass
