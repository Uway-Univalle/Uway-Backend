import os

import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_S3_REGION_NAME'),
    config = Config(signature_version= 's3v4')
)