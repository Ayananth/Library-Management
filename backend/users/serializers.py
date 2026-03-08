from rest_framework import serializers
from .models import User


from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

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
