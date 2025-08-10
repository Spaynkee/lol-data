from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from lolData.models import LeagueUser
from lolData.serializers.league_user_serializer import LeagueUserSerializer
from lolData.filters.league_user_filters import LeagueUserFilter


class LeagueUserViewSet(viewsets.ModelViewSet):
    queryset = LeagueUser.objects.all()
    serializer_class = LeagueUserSerializer
    permission_classes = [AllowAny]

    # Filtering, ordering, searching
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeagueUserFilter
    search_fields = ["name", "description"]
