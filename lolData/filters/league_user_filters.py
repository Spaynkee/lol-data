import django_filters
from lolData.models import LeagueUser


class LeagueUserFilter(django_filters.FilterSet):
    class Meta:
        model = LeagueUser
        fields = {"id": ["exact", "icontains"], "summoner_name": ["exact"]}
