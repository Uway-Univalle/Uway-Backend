import os

import boto3
from botocore.client import Config

s3 = boto3.resource(
    's3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
    config = Config(signature_version= 's3v4')
)