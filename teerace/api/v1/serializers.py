from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from accounts.models import UserProfile
from race.models import BestRun, Map, Run


class UserProfileSerializer(serializers.ModelSerializer):
    country = CountryField(allow_blank=True)
    
    class Meta:
        model = UserProfile
        fields = ("country", "points", "get_skin")


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    resource_uri = serializers.SerializerMethodField()

    def get_resource_uri(self, obj):
        return reverse("api:v1:user_detail", args=[obj.pk])

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "profile",
            "is_superuser",
            "is_staff",
            "id",
            "resource_uri",
        )


class MapSerializer(serializers.ModelSerializer):
    resource_uri = serializers.SerializerMethodField()

    def get_resource_uri(self, obj):
        return reverse("api:v1:map_detail", args=[obj.pk])

    class Meta:
        model = Map
        fields = (
            "name",
            "get_map_type",
            "author",
            "crc",
            "get_download_url",
            "run_count",
            "id",
            "resource_uri",
        )


class RunSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    resource_uri = serializers.SerializerMethodField()

    def get_resource_uri(self, obj):
        return reverse("api:v1:run_detail", args=[obj.pk])

    class Meta:
        model = Run
        fields = ("id", "user", "time", "checkpoints_list", "resource_uri")


class BestRunSerializer(serializers.ModelSerializer):
    run = RunSerializer()

    class Meta:
        model = BestRun
        fields = ("run",)
