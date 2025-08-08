"""test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.

"""

import os
import pytest
from unittest.mock import patch
from lolData.management.helpers.lolgather import LolGather
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def api_key():
    return os.getenv("RIOT_API_KEY")


@pytest.mark.django_db
class TestLolGatherGetMatchesList:
    """Contains all the test cases for get_matches_list()."""

    @patch("json.loads")
    @patch("requests.get")
    def test_max_game_index_default(self, mock_requests, mock_json, api_key):
        """Tests that our function works with max_game_index = 200"""
        mock_json.return_value = ["1234"]  # avoiding the break statement
        gather = LolGather()
        gather.get_matches_list("123", 400)
        assert mock_requests.call_count == 2
        assert mock_json.call_count == 2

        assert mock_requests.call_args_list[0].args[0] == (
            f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
            f"123/ids?start=0&queue=400&count=100&api_key={api_key}"
        )

        assert mock_requests.call_args_list[1].args[0] == (
            f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
            f"123/ids?start=100&queue=400&count=100&api_key={api_key}"
        )

    @patch("json.loads")
    @patch("requests.get")
    def test_max_game_index_fifty(self, mock_requests, mock_json, api_key):
        """Tests that our function works with max_game_index = 50"""
        gather = LolGather(50)
        gather.get_matches_list("123", 400)
        assert mock_requests.call_count == 1
        assert mock_json.call_count == 1

        assert mock_requests.call_args_list[0].args[0] == (
            f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
            f"123/ids?start=0&queue=400&count=50&api_key={api_key}"
        )


@pytest.mark.django_db
class TestLolGatherGetPuuid:
    """Contains all the test cases for get_puuid"""

    @patch("json.loads")
    @patch("requests.get")
    def test_get_puuid(self, mock_requests, mock_json, api_key):
        """Tests that we hit the correct endpoint for getting a players riot id."""
        gather = LolGather(100)
        gather.get_puuid("spaynkee")
        mock_requests.assert_called_once()
        mock_json.assert_called_once()

        assert mock_requests.call_args.args[0] == (
            f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
            f"spaynkee?api_key={api_key}"
        )


@pytest.mark.django_db
class TestLolGatherGetMatchData:
    """Contains all the test cases for get_match_data"""

    @patch("requests.get")
    def test_get_match_data(self, mock_requests, api_key):
        """Tests that we hit the correct endpoint for getting a players riot id."""
        gather = LolGather(100)
        gather.get_match_data("1234")
        mock_requests.assert_called_once()

        assert mock_requests.call_args.args[0] == (
            f"https://americas.api.riotgames.com/lol/match/v5/matches/NA1_1234?api_key={api_key}"
        )
