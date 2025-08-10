from rest_framework import serializers
from lolData.models import TeamData


class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = "__all__"
