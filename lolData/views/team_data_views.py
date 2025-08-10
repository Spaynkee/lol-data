from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from lolData.models import TeamData
from lolData.serializers.team_data_serializer import TeamDataSerializer
from lolData.filters.team_data_filters import TeamDataFilter


class TeamDataViewSet(viewsets.ModelViewSet):
    queryset = TeamData.objects.all()
    serializer_class = TeamDataSerializer
    permission_classes = [AllowAny]

    # Filtering, ordering, searching
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeamDataFilter
    search_fields = ["name", "description"]
