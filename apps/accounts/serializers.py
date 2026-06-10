from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


from .validators import validate_password_strength

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "full_name",
            "role",
            "password",
        ]

    def validate_password(self, value):
        return validate_password_strength(value)

    def validate_email(self, value):
        if User.objects.filter(
            email=value
        ).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop(
            "password"
        )

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user
    

from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        attrs["user"] = user

        return attrs
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError(
                "Invalid or expired refresh token."
            )



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()

    new_password = serializers.CharField()

    def validate_new_password(
        self,
        value
    ):
        validate_password_strength(
            value
        )
        return value