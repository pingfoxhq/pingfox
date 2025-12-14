from rest_framework.serializers import ModelSerializer, CharField, EmailField
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("avatar",)


class UserSerializer(ModelSerializer):
    email = EmailField(required=True)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    userprofile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "userprofile")
