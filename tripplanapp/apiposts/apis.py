

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.request import Request
from rest_framework import status
from typing import List
from rest_framework import serializers
from rest_framework.utils import model_meta
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema,extend_schema_field
from drf_spectacular.openapi import OpenApiParameter
from django.core.cache import cache
from django.urls import reverse
from tripplanapp.api.mixins import ApiAuthMixin
from PIL import Image

from tripplanapp.api.pagination import get_paginated_response,get_paginated_response_context,LimitOffsetPagination
from .selectors import get_user_post,post_list,post_detail
from .services import upload_image_file,add_image_data_PostModel
from .models import PostModel,PostVoteModel,CommentModel,ReplyModel,TripLocationModel,TripCategoryModel

class FileFieldSerializer(serializers.Serializer):
    image=serializers.FileField(required=True)

## upload image on view -> return image url after upload
class ImageUploadView(APIView,ApiAuthMixin):
    @extend_schema(request=FileFieldSerializer,responses=dict,tags=['post'])
    def post(self, request:Request):
        serializer = FileFieldSerializer(data=request.data)
        user=request.user
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            image = Image.open(image_file)
            result_ = upload_image_file(user_id=user.id,image_name=image_file.name,image=image)
            if result_["sucess"]:
                return Response({'message': 'Image received.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'message':'Upload file error.'},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        return Response({'message':'Image File not accepted.'}, status=status.HTTP_400_BAD_REQUEST)


class PostView(ApiAuthMixin,APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
    
    class FilterSerializer(serializers.Serializer):
        ## TODO : add more filter to get in explore
        location_name=serializers.CharField(required=False,max_length=100)
        # post_caption=serializers.CharField(required=False,max_length=100)
        # search=serializers.CharField(required=False,max_length=100) # add Filterset using postges searchvecto
        category=serializers.CharField(required=False,max_length=100)
        user_name=serializers.CharField(required=False,max_length=100)
        

    class InputPostUploadSerializer(serializers.Serializer):
        post_caption=serializers.CharField(max_length=1000,required=False)
        location_name=serializers.CharField()
        categories=serializers.CharField(max_length=1000,required=False)
        
        def validate(self, attrs):
            # 
            return super().validate(attrs)
    
    class OutputPostUploadSerializer(serializers.ModelSerializer):
        user_name=serializers.SerializerMethodField("get_user_name")
        location_name=serializers.SerializerMethodField("get_location_name")
        url=serializers.SerializerMethodField("get_url")


        class Meta:
            model=PostModel
            fields=("user_name","location_name","url","post_caption","files_urls","categories")

        @extend_schema_field(field=str)
        def get_user_name(self,post):
            return post.user.user_name
        @extend_schema_field(field=str)
        def get_location_name(self,post):
            return post.location.location
        @extend_schema_field(field=str)
        def get_url(self,post):
            request:Request=self.context.get("request")
            path=reverse("api:apiposts:post_detail",args=(post.slug))
            return request.build_absolute_uri(path)

    def get_serializer_class(self):
        return self.InputPostUploadSerializer

    @extend_schema(request=InputPostUploadSerializer,responses=OutputPostUploadSerializer,tags=['post'])
    def post(self, request:Request):
        serializer = self.InputPostUploadSerializer(data=request.data)
        user=request.user
        if serializer.is_valid():
            post_data = serializer.validated_data
            category_list=post_data.get("categories").split(",")
            res_=add_image_data_PostModel(user=user,post_caption=post_data.get("post_caption"),
                                     location_name=post_data.get("location_name"),
                                     categories=category_list)
            if res_["sucess"]:
                return Response(self.OutputPostUploadSerializer(res_["result"],context={"request":request}).data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'message':res_["result"]}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'message':'Post upload failed.'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(parameters=[FilterSerializer],responses=OutputPostUploadSerializer,tags=['post'])
    def get(self, request, *args, **kwargs):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        try:
            query=post_list(filters=filter_serializer.validated_data,user=request.user)
        except Exception as e:
            return Response({'detail':"Filter Error : "+str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputPostUploadSerializer,
            queryset=query,
            request=request,
            view=self,
        )



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLocationModel
        fields=("location","latitude","longitude")
        read_only_fields=("latitude","longitude")

class CategorysSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripCategoryModel
        fields=("category",)

class PostDetailView(ApiAuthMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset=PostModel.objects.all()
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class InputPostDetialSerializer(serializers.Serializer):
        post_id = serializers.IntegerField(required=True)
        post_caption = serializers.CharField(max_length=255,required=False)
        categories = serializers.ListField(child=serializers.CharField(max_length=255),required=False)
        location_name = serializers.CharField(max_length=255,required=False)

        def validate(self, attrs):
            ## TODO : remove invalid data chars from category and location
            return super().validate(attrs)
        
        def update(self, instance, validated_data):
            category_list=validated_data.pop("categories",[])
            cat_list=[]
            if category_list:
                for c in category_list:
                    category_intance=TripCategoryModel.objects.update_or_create(category=c)
                    cat_list.append(category_intance)
                instance.categories=cat_list

            ## Update location if it is provided
            location_data = validated_data.pop('location', None)
            if location_data:
                location_name=location_data.get("location")
                location, created = TripLocationModel.objects.update_or_create(location=location_name)
                instance.location=location
            
            ## save other 
            info = model_meta.get_field_info(instance)
            m2m_fields = []
            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    # m2m_fields.append((attr, value))
                    pass
                else:
                    setattr(instance, attr, value)

            instance.save()
                
            return instance

    class OutputPostDetailSerializer(serializers.ModelSerializer):
        url = serializers.SerializerMethodField("get_url")
        category_list=serializers.SerializerMethodField("get_category_list")
        user_profile_picture = serializers.SerializerMethodField("get_user_profile_picture")
        user_name = serializers.SerializerMethodField("get_user_name")
        location_name=LocationSerializer()
        comments_no=serializers.SerializerMethodField("get_comment_count")
        vote=serializers.SerializerMethodField('get_avg_vote')
        

        class Meta:
            model=PostModel
            fields=("url","user_name","user_profile_picture","category_list",
                    "location_name","files_urls",
                    "post_caption","created_at","vote","comments_no")
            read_only_fields=("files_urls","created_at")
            extra_kwargs={
                "post_caption": {"required": False},
                "location_name": {"required": False},
            }
        
        @extend_schema_field(field=list)
        def get_category_list(self,post):
            ## return list of all categoryes
            return post.categories
        
        @extend_schema_field(field=str)
        def get_user_profile_picture(self,post):
            return post.user.profile.profile_picture
        
        @extend_schema_field(field=str)
        def get_user_name(self,post):
            return post.user.user_name
        
        @extend_schema_field(field=int)
        def get_comment_count(self,post):
            return post.comments.count()

        @extend_schema_field(field=str)
        def get_url(self,post):
            request:Request=self.context.get("request")
            path=reverse("api:apiposts:post_detail",args=(post.slug))
            return request.build_absolute_uri(path)

        @extend_schema_field(field=float)
        def get_avg_vote(self,post):
            # return post.vote.aggregate(Avg('vote'))['vote__avg'] if post.vote.exists()
            return 10.0
        # The rest framework serializer's to_representation method allows the formatting of the json.
        def to_representation(self, instance):
            return super().to_representation(instance)
    
    def get_serializer_class(self):
        return self.InputPostDetialSerializer
    def get_queryset(self):
        return PostModel.objects.all()

    @extend_schema(responses=OutputPostDetailSerializer,tags=['post_detail'])
    def get(self, request, slug, *args, **kwargs):
        try:
            query=post_detail(slug=slug,user=request.user)
        except Exception as ex:
            return Response({"detail":"ERROR :"+str(ex)},status=status.HTTP_400_BAD_REQUEST)
        serializer=self.OutputPostDetailSerializer(query)
        return Response(serializer.data,status=status.HTTP_200_OK)
        # return super().get(request, *args, **kwargs)
    
    @extend_schema(request=InputPostDetialSerializer,responses=OutputPostDetailSerializer,tags=['post_detail'])
    def patch(self, request,slug, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        partial=True
        try:
            instance=post_detail(slug=slug,user=request.user)
            ## update the post
            serializer=self.InputPostDetialSerializer(instance,data=request.data,partial=partial)
            if serializer.is_valid():
                instance=serializer.update(instance=instance,validated_data=serializer.validated_data)
            else:
                return Response({"detail":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"detail":"ERROR :"+str(ex)},status=status.HTTP_400_BAD_REQUEST)
        
        out_serializer=self.OutputPostDetailSerializer(instance)
        return Response(out_serializer.data,status=status.HTTP_200_OK)            
        # return super().update(request, *args, **kwargs)
    
    @extend_schema(request=InputPostDetialSerializer,responses=OutputPostDetailSerializer,tags=['post_detail'])
    def put(self, request,slug, *args, **kwargs):
        partial=False
        try:
            instance=post_detail(slug=slug,user=request.user)
            ## update the post
            serializer=self.InputPostDetialSerializer(instance,data=request.data,partial=partial)
            if serializer.is_valid():
                instance=serializer.update(instance=instance,validated_data=serializer.validated_data)
            else:
                return Response({"detail":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"detail":"ERROR :"+str(ex)},status=status.HTTP_400_BAD_REQUEST)
        
        out_serializer=self.OutputPostDetailSerializer(instance)
        return Response(out_serializer.data,status=status.HTTP_200_OK)

    @extend_schema(tags=['post_detail'])
    def delete(self, request, slug,*args, **kwargs):
        try:
            instance=post_detail(slug=slug,user=request.user)
            instance.delete()
        except Exception as ex:
            return Response({"detail":"ERROR :"+str(ex)},status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail":"Post deleted"},status=status.HTTP_200_OK)
        # return super().delete(request, *args, **kwargs)




class VoteView():
    pass

class CommandView():
    pass

class ReplayView():
    pass

## return slug and image urls and every one can see ( like instagram explore )
class ExplorePostsView(APIView):
    def get(self, request:Request, *args, **kwargs):
        pass


