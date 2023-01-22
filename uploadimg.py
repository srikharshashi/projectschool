import boto3
from botocore.exceptions import ClientError
import os

BUCKET="drone-detect"

def upload_file(flightid,file_path):
    bucket_path=flightid
    s3_client = boto3.client('s3')
    
    object_name = flightid+os.path.basename(file_path)
    
    try:
        response = s3_client.upload_file(file_path, BUCKET, object_name)
    except ClientError as e:
        print(e)
        return ""
    URL="https://drone-detect.s3.us-east-1.amazonaws.com/"+object_name
    return URL

    
    