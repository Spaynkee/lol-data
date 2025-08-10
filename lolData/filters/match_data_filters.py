import django_filters
from lolData.models import MatchData


class MatchDataFilter(django_filters.FilterSet):
    class Meta:
        model = MatchData
        fields = {"id": ["exact", "icontains"], "player": ["iexact"]}
