import django_filters
from lolData.models import Champion


class ChampionFilter(django_filters.FilterSet):
    class Meta:
        model = Champion
        fields = {
            "id": ["exact", "icontains"],
        }
