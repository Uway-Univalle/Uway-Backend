from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #fields = "__all__"
        """exclude = [
            'last_login', 'is_superuser', 'is_staff', 'is_active',
            'date_joined', 'groups', 'user_permissions'
        ]"""
        exclude = ['groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user