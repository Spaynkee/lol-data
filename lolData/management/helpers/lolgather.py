"""lolgather.py class

This class contains all the methods needed by the main script and by the lolaccount class
to be able to gather league of legends data. It handles all API calls to the riot games api.

"""

import json
import time
import os
from typing import Dict
import requests
from .lolparser import LolParser
from .lollogger import LolLogger
from dotenv import load_dotenv

load_dotenv()


# pylint: disable=too-many-instance-attributes # This is okay.
class LolGather:
    """Contains all the methods and functions needed by our other classes to return data from riot

    Attributes:
        base_summoner_url (str): riot games api base endpoint for summoner
        account_name_url  (str): riot games api account name endpoint
        _base_match_url    (str): riot games api base endpoint for match
        _matches_url       (str): riot games api matches endpoint
        _match_url         (str): riot games api individual match endpoint


        accounts    (list: str): Holds a list of all accounts we collect data for
        match_id_list (list: str): Holds a list of games added this script run for logging
    """

    def __init__(self, max_game_index=200):
        self.base_summoner_url = "https://na1.api.riotgames.com/lol/summoner/v4/"
        self.account_name_url = "summoners/by-name/"
        self._base_match_url = (
            "https://americas.api.riotgames.com/lol/match/v5/matches/"
        )

        self.max_game_index = max_game_index

        self.lolparser = LolParser()
        self.accounts = self.lolparser.get_summoners()
        self.new_match_data: Dict[int, Dict] = {}
        self.match_id_list = ""
        self.logger = LolLogger(os.getenv("LOG_FILE_NAME"))
        self.api_key = os.getenv("RIOT_API_KEY")

    def get_matches_list(self, account_id: str, queue_type: int) -> list:
        """Gets an individual account's recently played match ids.

        Args:
            account_id: The account id associated with our account
            queue_type: The queue_type we want games for.

        Returns:
            A list containing match_ids from riot games.

        """
        game_index = 0
        player_matches = []

        if self.max_game_index <= 100:
            index_increment = self.max_game_index
        else:
            index_increment = 100

        # keeps looping until we get to the max_game_index
        # a higher max game index makes us check further back in time.
        while game_index < self.max_game_index:
            try:
                player_matches_response = requests.get(
                    "".join(
                        [
                            self._base_match_url,
                            "by-puuid/",
                            account_id,
                            "/ids?start=",
                            str(game_index),
                            "&queue=",
                            str(queue_type),
                            "&count=",
                            str(index_increment),
                            "&api_key=",
                            self.api_key,
                        ]
                    ),
                    timeout=200,
                )

                player_matches_response.raise_for_status()
                player_matches_response_list = json.loads(player_matches_response.text)

                if len(player_matches_response_list) == 0:
                    break

                # we want to only append the games, not the list.
                player_matches += player_matches_response_list

                game_index += 100

            except requests.exceptions.RequestException as exc:
                self.logger.log_critical("Get_account_info broke")
                if exc.response.status_code == 403:
                    self.logger.log_critical("Api key is probably expired")
                elif exc.response.status_code == 429:
                    self.logger.log_warning("Well that's an unfortunate timeout.")
                    time.sleep(10)
                else:
                    self.logger.log_critical(exc)

            time.sleep(0.1)

        return player_matches

    def get_match_data(self, match_id: int) -> str:
        """Gets an individual matches data

        Args:
            match_id: The match id we're getting data for

        Returns:
            The text form of the json object we get from riot games,
            so that it can be stored in the json_data table.

        """
        try:
            self.logger.log_info("".join(["getting match data for ", str(match_id)]))

            # add match_id to match list
            self.match_id_list = self.match_id_list + " " + str(match_id)

            time.sleep(0.08)  # this should keep us around the 20 per 1 second limit.

            matches_response = requests.get(
                "".join(
                    [
                        self._base_match_url,
                        f"NA1_{str(match_id)}",
                        "?api_key=",
                        self.api_key,
                    ]
                ),
                timeout=200,
            )

            matches_response.raise_for_status()
            match_json = matches_response.json()

            self.new_match_data[match_id] = match_json

            return match_json

        except requests.exceptions.RequestException as exc:
            self.logger.log_critical(exc)
            self.logger.log_warning("Get_match_data broke, trying again")
            time.sleep(10)
            self.get_match_data(match_id)

        return ""

    @staticmethod
    def get_unstored_match_ids(prev_matches: list, new_matches: dict) -> list:
        """Compares a set of previous match ids with the data we return from riot to determine
        which matches we will need to get data for.

        Args:
            prev_matches: the list of matches we already have data for.
            new_matches: A dict containing recent game ids. queue type is the key.
            match_types: A list of the match types to include in the comparison.

        Returns:
            A list (int) of match ids a player was in, but that we don't have stored yet.
        """

        unstored_match_ids = []

        for _, match_list in new_matches.items():
            for match in match_list:
                if int(match[4:]) not in prev_matches:
                    unstored_match_ids.append(int(match[4:]))

        return unstored_match_ids

    def get_puuid(self, account_name: str) -> str:
        """Gets the puuid for this account name from riot.

        Args:
            account_name: the account name we're getting the account_id for

        Returns:
            The account_id associated with this account from riot
        """

        try:
            account_response = requests.get(
                "".join(
                    [
                        self.base_summoner_url,
                        self.account_name_url,
                        account_name,
                        "?api_key=",
                        self.api_key,
                    ]
                ),
                timeout=200,
            )
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            return account_data["puuid"]
        except requests.exceptions.RequestException as exc:
            if exc.response.status_code == 403:
                self.logger.log_critical("Api key is probably expired")

            self.logger.log_critical("get_user_id broke")

        return ""

    def get_match_timeline(self, match_id: int) -> str:
        """Gets an individual matches timeline

        Args:
        match_id: The match id we're getting the timeline of.

        Returns:
        The text form of the json object we get from riot games,
        so that it can be stored in the timeline_data table.

        """
        try:
            self.logger.log_info(
                "".join(["getting match timeline for ", str(match_id)])
            )

            time.sleep(0.08)  # this should keep us around the 20 per 1 second limit.

            timeline_response = requests.get(
                "".join(
                    [
                        self._base_match_url,
                        f"NA1_{str(match_id)}",
                        "/timeline",
                        "?api_key=",
                        self.api_key,
                    ]
                ),
                timeout=200,
            )

            timeline_response.raise_for_status()
            timeline_json = timeline_response.json()

            return timeline_json

        except requests.exceptions.RequestException as exc:
            self.logger.log_critical(exc)
            self.logger.log_warning("Get_match_data broke, trying again")
            time.sleep(10)
            return self.get_match_timeline(match_id)

        return ""

    def get_league_user_data(self, account_name: str):
        """Gets an accounts info for a particular username

        Args:
            account_name: the account name we're storing the puuid for

        Returns:
            The info riot has associated with this account.
        """
        try:
            account_response = requests.get(
                "".join(
                    [
                        self.base_summoner_url,
                        self.account_name_url,
                        account_name,
                        "?api_key=",
                        self.api_key,
                    ]
                ),
                timeout=200,
            )
            account_response.raise_for_status()
            account_data = json.loads(account_response.text)
            return account_data
        except requests.exceptions.RequestException as exc:
            if exc.response.status_code == 403:
                self.logger.log_critical("Api key is probably expired")

            self.logger.log_critical("get_league_user_data  broke")

        return ""
