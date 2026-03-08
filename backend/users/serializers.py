from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data.get("email"),
                password=validated_data["password"],

        )
        return user
    

class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["avatar"]
