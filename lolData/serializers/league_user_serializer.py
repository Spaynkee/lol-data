from rest_framework import serializers
from lolData.models import LeagueUser


class LeagueUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeagueUser
        fields = "__all__"
