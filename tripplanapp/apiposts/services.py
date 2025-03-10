
import base64
from PIL import Image
from tempfile import TemporaryFile
import uuid
import io
from typing import List
from django.core.cache import cache
from celery.result import AsyncResult
from .utils.image_features import image_coordinates
import boto3
from django.core.files.base import ContentFile
from django.core.files import File
from .models import TripLocationModel,TripCategoryModel,PostModel,PostVoteModel,CommentModel,ReplyModel

from tripplanapp.users.models import BaseUser
from .tasks import upload_image_to_s3,image_vector_features

def upload_image_file(*, user_id:int,image_name:str,image:Image ) -> dict:
    # Process the image and upload to S3
    try:
        fp = TemporaryFile()
        image.save(fp, format=image.format)
        fp.seek(0)
        with open(image_name, 'rb') as file:
            picture = File(file)

        thumb_io = io.BytesIO()
        image.save(thumb_io, format=image.format)
        img_byte_arr = thumb_io.getvalue()
        ########################### START CELERY USE
        ### refrence => https://stackoverflow.com/questions/71116738/how-to-use-celery-to-upload-files-in-django
        ### Send image to feature extraction model
        ## TODO : useing celery
        img_feature_task=image_vector_features.delay(kwarg={"image_data":img_byte_arr.decode('utf-8'),"image_name":image_name})
        img_featureTask_id=img_feature_task.id
        ## TODO : without celery
        img_feature_task=image_vector_features(image_data=img_byte_arr.decode('utf-8'),image_name=image_name)
        img_featureTask_id=img_feature_task
        ########################### END CLELRY USE
        cache.set("user_imageFeature_TaskId"+str(user_id), img_featureTask_id, timeout=1200)  # 20 min

        ## extract image location 
        location_features=image_coordinates(image=image)
        if location_features["sucess"]:
            cache.set("user_imagelocation"+str(user_id), location_features["result"], timeout=1200)  # 20 min
        else:
            ## TODO : base on location_name to get GPS
            return location_features  ## {"sucess":False,"result":msg}

        ##### upload image to s3
        
        bucket_name = 'your-s3-bucket-name'  # TODO : Replace with your bucket name
        # s3 = boto3.client('s3')
        # s3.upload_fileobj(ContentFile(img_byte_arr), bucket_name, image_name)
        # Return the URL of the uploaded image
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_name}"
        # Cache the task ID
        cache.set("user_post_imageUrl"+str(user_id), str(image_url), timeout=1200)  # 20 min

        return {"sucess":True,"result":image_url}
    except Exception as e:
        return {"sucess":False,"result":str(e)}
    
    

def add_image_data_PostModel(*, user:BaseUser,post_caption:str,location_name:str,categories:List[str]) -> dict:
    user_id=user.id
    
    location_features=cache.get("user_imagelocation"+str(user_id))
    if location_features:
        GPSLatitude=location_features["GPSLatitude"]
        GPSLongitude=location_features["GPSLongitude"]
        ## create or get_object location
        location_obj, created = TripLocationModel.objects.get_or_create(location=location_name,
                                                                        latitude=GPSLatitude,
                                                                        longitude=GPSLongitude)
    else:
        return {"sucess":False,"result":"Not found location."}
    
    ## DONE : get result from task
    image_url=cache.get("user_post_imageUrl"+str(user_id)) ## get image_url from cache that seted in {{ upload_image_file }} 
    if not image_url:
        return {"sucess":False,"result":"Not found uploded Image."}
    ## create category
    category_instances=[]
    for c in categories:
        category_instances.append(TripCategoryModel.objects.get_or_create(name=c)[0])
    
    ####################### START [image features]
    
    img_featureTask_id=cache.get("user_imageFeature_TaskId"+str(user_id)) ##
    ## TODO : using celery
    # res = AsyncResult(img_featureTask_id,app=image_vector_features)
    # if res.state == 'SUCCESS':
    #     image_features=res.get()
    # else:
    #     ## TODO : feature extraction Error handeling
    #     pass
    ## TODO : without celery
    image_features=img_featureTask_id
    ####################### END [image features]
    ## Create random slug
    while True:
        slug = uuid.uuid4().hex[10]
        exist_slug=PostModel.objects.filter(slug=slug).exists()
        if not exist_slug:
            break

    # Save the image URL and location to the PostModel
    post = PostModel.objects.create(location=location_obj,user=user,slug=str(slug),
                                    post_caption=post_caption,files_urls=image_url,
                                    post_features=image_features,categories=category_instances,
                                    avg_post_vote=10.0)
    post.save()
    return {"sucess":True,"result":post}



def update_post_features():
    pass

def update_post_fields(*,user):
    pass


def add_post_vote():
    pass

def add_comment():
    pass

def add_reply():
    pass
