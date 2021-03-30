import json
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Content, Category


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "first_name", "last_name")

    def get_full_name(self, user):
        return user.get_full_name()


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user_id')
    full_name = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ("id", "full_name", "email", "first_name", "last_name",
                  "address",  "phone_no", "city", "state", "country", "pin_code")

    def get_full_name(self, profile):
        return profile.user.get_full_name()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class ContentSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Content
        fields = "__all__"
