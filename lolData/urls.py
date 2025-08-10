"""
URL configuration for lolData project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lolData.views.champion_views import ChampionViewSet
from lolData.views.team_data_views import TeamDataViewSet
from lolData.views.match_data_views import MatchDataViewSet
from lolData.views.league_user_views import LeagueUserViewSet


router = DefaultRouter()
router.register(r"champions", ChampionViewSet, basename="champion")
router.register(r"team_data", TeamDataViewSet, basename="team_data")
router.register(r"match_data", MatchDataViewSet, basename="match_data")
router.register(r"league_user", LeagueUserViewSet, basename="league_user")

urlpatterns = [
    path("api/", include(router.urls)),
]
