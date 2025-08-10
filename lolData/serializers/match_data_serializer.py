from rest_framework import serializers
from lolData.models import MatchData


class MatchDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchData
        fields = "__all__"
