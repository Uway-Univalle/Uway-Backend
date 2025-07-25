import os

from rest_framework import serializers

from core.aws.helpers import create_presigned_url
from users.models import User, UserDocument, UserType


class UserSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(
            allow_empty_file=False, allow_null=False, required=False
        ),
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'id','first_name', 'last_name', 'username', 'email', 'personal_id', 'address', 'phone', 'code',
            'user_type', 'passenger_type', 'college', 'is_verified', 'date_joined',
            'last_login', 'password', 'attachments'
        ]
        extra_kwargs = {
            'password' : {'write_only' : True},
            'date_joined' : {'read_only' : True},
            'last_login' : {'read_only' : True}
        }



class UserDocumentSerializer(serializers.ModelSerializer):
    presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = UserDocument
        fields = ['id', 'url', 'presigned_url']

    def get_presigned_url(self, obj):
        key = obj.url.replace(f"https://{os.environ.get('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/", "")
        return create_presigned_url(key)

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id','name', 'description']