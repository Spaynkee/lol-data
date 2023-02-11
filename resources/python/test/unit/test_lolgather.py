""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.


Don't forget -- Run this from the root folder /lol-data and use the command
python -m unittest discover resources/python/test

"""

#pylint: disable=import-error #False positive.
import unittest
from unittest.mock import patch
from resources.python.classes.lolgather import LolGather
from resources.python.classes.lolconfig import LolConfig

class TestLolGatherGetMatchesList(unittest.TestCase):
    """ Contains all the test cases for get_matches_list().
    """
    def setUp(self):
        """ set up method for our test cases. This runs for every test case. Instantiates the
            config object so we can get our api key.

        """
        self.config = LolConfig()

    @patch('json.loads')
    @patch('requests.get')
    def test_max_game_index_default(self, mock_requests, mock_json):
        """ Tests that our function works with max_game_index = 200

        """

        mock_json.return_value = ["1234"] # avoiding the break statement
        gather = LolGather()
        gather.get_matches_list("123", 400)
        self.assertEqual(mock_requests.call_count, 2)
        self.assertEqual(mock_json.call_count, 2)

        self.assertEqual(mock_requests.call_args_list[0].args[0],\
                "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"+\
                f"123/ids?start=0&queue=400&count=100&api_key={self.config.api_key}")


        self.assertEqual(mock_requests.call_args_list[1].args[0],\
                "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"+\
                f"123/ids?start=100&queue=400&count=100&api_key={self.config.api_key}")


    @patch('json.loads')
    @patch('requests.get')
    def test_max_game_index_fifty(self, mock_requests, mock_json):
        """ Tests that our function works with max_game_index = 50

        """

        gather = LolGather(50)
        gather.get_matches_list("123", 400)
        self.assertEqual(mock_requests.call_count, 1)
        self.assertEqual(mock_json.call_count, 1)

        self.assertEqual(mock_requests.call_args_list[0].args[0],\
                "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"+\
                f"123/ids?start=0&queue=400&count=50&api_key={self.config.api_key}")

class TestLolGatherGetPuuid(unittest.TestCase):
    """ Contains all the test cases for get_puuid

    """

    def setUp(self):
        """ set up method for our test cases. This runs for every test case. Instantiates the
            config object so we can get our api key.

        """
        self.config = LolConfig()

    @patch('json.loads')
    @patch('requests.get')
    def test_get_puuid(self, mock_requests, mock_json):
        """ Tests that we hit the correct endpoint for getting a players riot id.

        """

        gather = LolGather(100)
        gather.get_puuid("spaynkee")
        mock_requests.assert_called_once()

        mock_json.assert_called_once()

        self.assertEqual(mock_requests.call_args.args[0],\
            "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+\
            f"spaynkee?api_key={self.config.api_key}")

class TestLolGatherGetMatchData(unittest.TestCase):
    """ Contains all the test cases for get_match_data

    """
    def setUp(self):
        """ set up method for our test cases. This runs for every test case. Instantiates the
            config object so we can get our api key.

        """
        self.config = LolConfig()

    @patch('requests.get')
    def test_get_match_data(self, mock_requests):
        """ Tests that we hit the correct endpoint for getting a players riot id.

        """

        gather = LolGather(100)
        gather.get_match_data("1234")
        mock_requests.assert_called_once()

        self.assertEqual(mock_requests.call_args.args[0],\
            "https://americas.api.riotgames.com/lol/match/v5/matches/NA1_1234"+\
            f"?api_key={self.config.api_key}")

if __name__ == "__main__":
    unittest.main()
