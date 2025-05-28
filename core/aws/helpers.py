from botocore.exceptions import ClientError

from core.aws.setup import s3
import os

def upload_file_to_s3(file, key):
    s3.Bucket(os.environ.get('AWS_STORAGE_BUCKET_NAME')).put_object(Key=key, Body=file)
    url = f"https://{os.environ.get('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/{key}"
    return url

def create_presigned_url(key, expiration=3600):
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params = {'Bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME'), 'Key': key},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        return None

    return response