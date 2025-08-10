import django_filters
from lolData.models import TeamData


class TeamDataFilter(django_filters.FilterSet):
    class Meta:
        model = TeamData
        fields = {
            "match_id": ["exact", "icontains"],
        }
