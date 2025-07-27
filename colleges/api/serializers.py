from rest_framework import serializers

from colleges.models import College


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'
        extra_kwargs = {
            'logo': {'read_only': True},
            'is_verified': {'read_only': True},
        }

class CollegeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=320, required=False, allow_blank=True)
    colors = serializers.ListField(
        child=serializers.CharField(max_length=7, allow_blank=True, required=False),
        required=True,
        allow_empty=False
    )
    logo_img = serializers.FileField(
        required=True,
        allow_empty_file=False,
        allow_null=False
    )

class ReportRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y'])
    end_date = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y'])
