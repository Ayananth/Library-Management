from rest_framework import serializers
import re

from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    RESERVED_USERNAMES = {"admin", "root", "support", "help", "me"}

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_username(self, value):
        username = value.strip()

        if username != value:
            raise serializers.ValidationError("Username cannot start or end with spaces.")

        if len(username) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")

        if len(username) > 30:
            raise serializers.ValidationError("Username must be at most 30 characters long.")

        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", username):
            raise serializers.ValidationError(
                "Username must start with a letter and contain only letters, numbers, and underscores."
            )

        if "__" in username:
            raise serializers.ValidationError("Username cannot contain consecutive underscores.")

        if username.lower() in self.RESERVED_USERNAMES:
            raise serializers.ValidationError("This username is not allowed.")

        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("A user with that username already exists.")

        return username

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        return user

class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["avatar"]


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "avatar"]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Invalid or expired refresh token."})

        return attrs
