from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from lolData.models import MatchData
from lolData.serializers.match_data_serializer import MatchDataSerializer
from lolData.filters.match_data_filters import MatchDataFilter


class MatchDataViewSet(viewsets.ModelViewSet):
    queryset = MatchData.objects.all()
    serializer_class = MatchDataSerializer
    permission_classes = [AllowAny]

    # Filtering, ordering, searching
    filter_backends = [DjangoFilterBackend]
    filterset_class = MatchDataFilter
    search_fields = ["name", "description"]
    pagination_class = None
