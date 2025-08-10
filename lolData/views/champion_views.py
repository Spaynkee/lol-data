from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from lolData.models import Champion
from lolData.serializers.champion_serializer import ChampionSerializer
from lolData.filters.champion_filters import ChampionFilter


class ChampionViewSet(viewsets.ModelViewSet):
    queryset = Champion.objects.all()
    serializer_class = ChampionSerializer
    permission_classes = [AllowAny]

    # Filtering, ordering, searching
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChampionFilter
    search_fields = ["name", "description"]
