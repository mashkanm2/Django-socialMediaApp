
import base64
from PIL import Image
import io
import uuid
from django.core.cache import cache
from tripplanapp.apiposts.models import PostModel
from tripplanapp.users.models import BaseUser
from celery.result import AsyncResult
from .utils.image_features import image_coordinates

from .tasks import upload_image_to_s3,image_vector_features

def upload_image_file(*, user_id:int,image_name:str,image:Image ) -> str:
    
    image_io=io.BytesIO()
    image.save(image_io,format=image.format)
    # Generate a unique key for the task ID
    # unique_key = str(uuid.uuid4())

    ### refrence => https://stackoverflow.com/questions/71116738/how-to-use-celery-to-upload-files-in-django
    image_data=base64.b64encode(image_io.getvalue()).decode('utf-8')
    upload_task = upload_image_to_s3.delay(image_data, image_name)
    # Cache the task ID
    cache.set(user_id, str(upload_task.id), timeout=1200)  # 20 min

    return str(upload_task.id)

def add_image_data_PostModel(*, image, user_id:int) -> None:
    ## TODO : extract features
    location_features=image_coordinates(image=image)
    if location_features["sucess"]:
        pass
        ## create or get_object location
    else:
        print("Error extracting image features")
    ## TODO : get result from task
    task_id = cache.get(user_id)  ## get task id from cache that seted on {{ upload_image_file }} function
    if not task_id:
        return None
    res = AsyncResult(task_id,app=upload_image_to_s3)

    if res.state == 'SUCCESS':
        res_=res.get()
        
        if not res_["sucess"]:
            ## TODO : rise error in boto3
            pass
        image_url = res_["result"]
    else:
        ## TODO : wait for secends or raise error
        pass
    

    ## create category
    
    
    # Save the image URL and location to the PostModel
    post = PostModel.objects.create(image_url=image_url, location=location, task_id=task_id)



def add_category_post():
    pass

def add_location_post():
    pass


def upload_post():
    pass

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
