

# from celery import shared_task
from botocore.exceptions import NoCredentialsError
from django.core.cache import cache

import os

def upload_image_to_s3(*, image_data, image_name) -> dict:
    import PIL.Image as Image
    import boto3
    import io
    import base64
    from django.core.files.base import ContentFile
    from django.core.files import File

    # This function is now handled in the upload_image task
    # Process the image and upload to S3
    try:
        byte_data = image_data.encode(encoding='utf-8')
        image_bytes = base64.b64decode(byte_data)
        # img = Image.open(io.BytesIO(image_bytes))
        # img.save(image_name, format=img.format)
        # with open(image_name, 'rb') as file:
        #     picture = File(file)

        if image_data:
            s3 = boto3.client('s3')
            bucket_name = 'your-s3-bucket-name'  # TODO : Replace with your bucket name
            s3.upload_fileobj(ContentFile(image_bytes), bucket_name, image_name)
            # Return the URL of the uploaded image
            image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_name}"
            return {"sucess":True,"result":image_url}
            
    except NoCredentialsError:
        return {"sucess":False,"result":None}



def image_vector_features(*, image_data, image_name)-> list:
    import base64
    import PIL.Image as Image
    import io
    import numpy as np
    try:
        byte_data = image_data.encode(encoding='utf-8')
        image_bytes = base64.b64decode(byte_data)
        if image_data:
            img = Image.open(io.BytesIO(image_bytes))
            img.save(image_name, format=img.format)
            ## TODO : send to extraction model
            # image_vector = extract_image_features(image_name)
            temp_result=np.random.random(size=[512,])

            return temp_result.tolist()
        
    except Exception as e:
        ## raise error
        return []
