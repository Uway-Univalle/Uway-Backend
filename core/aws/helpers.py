from botocore.exceptions import ClientError

from core.aws.setup import s3
import os

def upload_file_to_s3(file, key):
    """
    Uploads a file to Amazon S3
    :param file: File to upload
    :param key: Path where the file is going to be stored in the cloud. Ej. 'folder/nested/file.ext'
    :return: The url of the file.
    """
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')

    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=file
    )
    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    return url

def create_presigned_url(key, expiration=3600):
    """
    Create a presigned url so the frontend can render private files. The
    generated url has an expiration time. Default to 1 hour.
    :param key: Path where the file is stored in the cloud. Ej. 'folder/nested/file.ext'
    :param expiration: Expiration time in seconds
    :return: The presigned url of the file
    """
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params = {'Bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME'), 'Key': key},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        return None

    return response

def delete_file_from_s3(key):
    """
    Elimina un archivo de Amazon S3.
    :param key: Ruta del archivo en S3. Ej. 'folder/nested/file.ext'
    :return: True si se elimina correctamente, False si hay error.
    """
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError:
        return False