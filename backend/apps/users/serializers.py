from rest_framework import serializers
from .models import Profile


class LoginSerializer(serializers.Serializer):
    """로그인 요청 데이터 검증"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=6)


class ProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 응답 데이터"""
    class Meta:
        model = Profile
        fields = ['id', 'role', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
