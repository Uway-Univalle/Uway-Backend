import os

from rest_framework import serializers

from core.aws.helpers import create_presigned_url
from users.models import User, UserDocument


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'personal_id', 'address', 'phone', 'code',
            'user_type', 'passenger_type', 'college', 'is_verified', 'date_joined',
            'last_login', 'password'
        ]
        extra_kwargs = {
            'password' : {'write_only' : True},
            'date_joined' : {'read_only' : True},
            'last_login' : {'read_only' : True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserDocumentSerializer(serializers.ModelSerializer):
    presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = UserDocument
        fields = ['id', 'url', 'presigned_url']

    def get_presigned_url(self, obj):
        key = obj.url.replace(f"https://{os.environ.get('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/", "")
        return create_presigned_url(key)