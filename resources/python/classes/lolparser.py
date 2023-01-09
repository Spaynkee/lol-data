""" lolparser.py class

This class contains all the methods needed to store and retrieve league of legends
data to or from our databases. It handles all db transactions during the script run.

"""
import time
from typing import Tuple, Dict
from datetime import datetime as date
from .lolconfig import LolConfig
from .loldb import LolDB
from .lolmongo import LolMongo
from .lollogger import LolLogger
from .models import TeamData, MatchData, JsonData, Champions, Items, ScriptRuns, LeagueUsers,\
        JsonTimeline

#pylint: disable=too-many-public-methods # No way around this one right now. Maybe a refactor later
class LolParser():
    """ Contains all the methods and functions needed by loldata.py and classes/lolaccount.py
        to store data into the database.
    """

    def __init__(self):
        self.config = LolConfig()
        self.logger = LolLogger(self.config.log_file_name)

        self.our_db = LolDB(self.config.db_host, self.config.db_user, self.config.db_pw,\
                self.config.db_name)

        self.mongodb = LolMongo(self.config.mongo_host, self.config.mongo_user,\
                self.config.mongo_pw, self.config.mongo_name)

    def select_previous_match_data_rows(self, account_name: str) -> list:
        """ Gets the matches we already have in match_data and returns the match data as a list

            Args:
                account_name: the name of the player we're getting matches for

            Returns:
                A list of match_data row objects

        """

        return self.our_db.session.query(MatchData).filter_by(player=account_name).all()

    def select_previous_team_data_rows(self) -> list:
        """ Gets the matches we already have in team_data and returns a list of row objects

            Returns:
                A list of team_data row objects

        """
        return self.our_db.session.query(TeamData).all()

    def get_previous_team_data_match_ids(self) -> list:
        """ Creates and Returns a list of the match_ids already in team_data

            Returns:
                A list of integers containing all match_ids currently in team_data
        """
        team_data_match_history = self.select_previous_team_data_rows()
        previous_team_data_matches = []

        for row in team_data_match_history:
            previous_team_data_matches.append(row.match_id)

        return previous_team_data_matches

    def get_previous_player_match_data_ids(self, name: str) -> list:
        """ Creates and returns a list containing all the match_ids for each row in match_data

            Args:
                name: the name of the player we're getting match_data_for

            Return:
                A list of integers containing all match_ids currently stored for this player
        """
        player_match_history = self.select_previous_match_data_rows(name)
        previous_player_matches = []


        for match in player_match_history:
            previous_player_matches.append(match.match_id)

        return previous_player_matches

    def insert_match_data_row(self, match_data: dict, account_name: str,\
            account_id: str):

        """ Parses through a large dict and inserts data into the match_data table.

            Args:
                match_data: a large dict containing all the match data
                account_name: the player we're updating for
                account_id: the id of the player so we can determine participant index

        """
        # This object will store all the data we intend to save.
        match_obj = MatchData()
        match_data = match_data['info']

        participant_index = self.get_participant_index(match_data['participants'],\
                account_id)

        match_obj.match_id = match_data['gameId']
        match_obj.player = account_name

        participant = match_data['participants'][participant_index]
        match_obj.champion = participant['championId']

        match_obj.kills = participant['kills']
        match_obj.deaths = participant['deaths']
        match_obj.assists = participant['assists']
        match_obj.wards_placed = participant['wardsPlaced']
        match_obj.damage_to_champs = participant['totalDamageDealtToChampions']
        match_obj.damage_to_turrets = participant['damageDealtToTurrets']
        match_obj.vision_wards_bought = participant['visionWardsBoughtInGame']
        match_obj.wards_killed = participant['wardsKilled']

        match_obj.champion_name = self.get_champ_name(participant['championId'])

        match_obj.first_blood, match_obj.first_blood_assist =\
                self.get_first_blood_kill_assist(participant)

        role = self.get_role(participant)

        match_obj.role = role

        match_obj.gold_per_minute = self.get_gold_per_minute(participant,\
                match_data['gameDuration'])
        match_obj.creeps_per_minute = self.get_cs_per_minute(participant,\
                match_data['gameDuration'])
        match_obj.xp_per_minute = self.get_xp_per_minute(participant,\
                match_data['gameDuration'])

        match_obj.enemy_champion, match_obj.enemy_champion_name  = self.get_enemy_champ(role,\
                participant_index, match_data['participants'])

        match_obj.items = self.get_items(participant)
        match_obj.perks = self.get_perks(participant)

        self.our_db.session.add(match_obj)
        self.our_db.session.commit()

    def insert_team_data_row(self, match_data: dict, account_name: str, account_id: str):
        """ Goes through a match_data dict, parses out information, and stores into team_data table

            Args:
                match_data: a large dict containing match data from riot api
                account_name: the name of the player we're storing games for
                account_id: the id of the player we're storing games for

        """

        # determine ally and enemy team data
        team_data, enemy_team_data, team_id = self.get_team_data(match_data, account_id)
        team_obj = TeamData()

        match_data = match_data['info']
        # get some team information.
        team_obj.participants = account_name

        if team_data['win']:
            team_obj.win = 'Win'
        else:
            team_obj.win = 'Fail'

        objectives = team_data['objectives']

        team_obj.first_blood = objectives['champion']['first']
        team_obj.first_baron = objectives['baron']['first']
        team_obj.first_tower = objectives['tower']['first']
        team_obj.first_rift_herald = objectives['riftHerald']['first']
        team_obj.first_dragon = objectives['dragon']['first']
        team_obj.first_inhib = objectives['inhibitor']['first']

        team_obj.ally_rift_herald_kills = objectives['riftHerald']['kills']
        team_obj.ally_dragon_kills = objectives['dragon']['kills']
        team_obj.inhib_kills = objectives['inhibitor']['kills']

        team_obj.game_version = match_data['gameVersion']
        team_obj.match_id = match_data['gameId']

        # sometimes we need enemy info too.
        enemy_objectives = enemy_team_data['objectives']
        team_obj.enemy_dragon_kills = enemy_objectives['dragon']['kills']
        team_obj.enemy_rift_herald_kills = enemy_objectives['riftHerald']['kills']

        team_obj.bans = self.get_team_bans(team_data['bans'])
        team_obj.enemy_bans = self.get_team_bans(enemy_team_data['bans'])

        team_obj.allies, team_obj.enemies = self.get_allies_and_enemies(team_id,\
                match_data['participants'])

        team_obj.start_time, team_obj.duration = self.get_start_time_and_duration(\
                match_data['gameCreation'], match_data['gameDuration'])

        self.our_db.session.add(team_obj)
        self.our_db.session.commit()

    def update_team_data_row(self, match: int, account_name: str):
        """ if the match we're trying to insert into team_data already exists, we update the
            participants field instead, since our current player was in the game with
            a previous player.

            Args:
                match: the match_id we're updating
                account_name: the player we're updating the table for

        """

        existing_team_data_row = self.our_db.session.query(TeamData).filter_by(match_id=match).one()

        existing_team_data_row.participants = \
                f"{existing_team_data_row.participants}, {account_name}"

        self.our_db.session.commit()

    @staticmethod
    def get_participant_index(participant_identities: dict, puuid: str) -> int:
        """ Gets a participants index based on their puuid

            Args:
                participant_identities: a dictionary containing all 10 players identities
                puuid: the puuid of the player we're getting the index of

            Returns:
                The index of our accounts participant

        """
        for index, player in enumerate(participant_identities):
            if player['puuid'] == puuid:
                return index

        return -1

    def get_summoner_names(self) -> list:
        """ Creates and returns a list of summoner names that we have stored in the league_users
            table.

            Returns:
                A list of names stored in the league_users table
        """

        league_users = self.our_db.session.query(LeagueUsers).all()
        return [user.summoner_name for user in league_users]


    def store_json_data(self, match: int, json_formatted_string: str):
        """ Stores the json data for a single match into the json mongodb collection.

            Args:
                match: The match id we're storing data for
                json_formatted_string: The actual json data to be stored
        """
        json_doc = self.mongodb.json.find_one({'_id': match})
        json_row = self.our_db.session.query(JsonData).filter_by(match_id=match).first()

        if not json_doc and not json_row:
            insert_dict = {'_id': match, 'json_data': json_formatted_string}
            self.mongodb.json.insert_one(insert_dict)

            # leaving sql code in for a week so we are sure everything works.
            self.our_db.session.add(JsonData(match_id=match, json_data=json_formatted_string))
            self.our_db.session.commit()
        else:
            self.logger.log_warning("Json already stored.")

    def store_json_timeline(self, match: int, json_formatted_string: str):
        """ Stores the json data for a match timeline into the json_timeline table.

            Args:
                match: The match id we're storing data for
                json_formatted_string: The actual json data to be stored
        """

        timeline_json_doc = self.mongodb.timeline_json.find_one({'_id': match})
        json_row = self.our_db.session.query(JsonTimeline).filter_by(match_id=match).first()

        if not timeline_json_doc and not json_row:
            insert_dict = {'_id': match, 'json_timeline': json_formatted_string}
            self.mongodb.timeline_json.insert_one(insert_dict)

            # leaving sql code in there for now.
            self.our_db.session.add(JsonTimeline(match_id=match,\
                    json_timeline=json_formatted_string))
            self.our_db.session.commit()
        else:
            self.logger.log_warning("Json already stored for timeline.")

    def store_run_info(self, source: str):
        """ Creates a new row in the script_runs table

            Args:
                source: The source of the script run (Daily, Manual, ManualWeb)
        """
        time_started = date.now().strftime("%Y-%m-%d %H:%M:%S")
        self.our_db.session.add(\
                ScriptRuns(source=source, start_time=time_started, status="Running"))


    def update_run_info(self, status: str, matches: str, message: str):
        """ Updates the currently running row in script_runs

            Args:
                status:  The status of the run (Failed, Success)
                matches: A string containing all the matches that were added by this script run
                message: Any message explaining the status of the run (exception if failed, etc)

        """

        script_row = self.our_db.session.query(ScriptRuns).filter_by(status="Running").first()
        script_row.status = status
        script_row.message = message
        script_row.end_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
        script_row.matches_added = matches

        self.our_db.session.commit()

    @staticmethod
    def get_gold_per_minute(participant: object, game_duration) -> int:
        """ Gets the gold per minute for a player based on their gold earned.

            Args:
                participant: A participant object from riot.
                game_duration: The length of the game in milliseconds.

            Returns:
                The gold per minute for a player, for this match.

        """
        return participant['goldEarned'] / ((game_duration/1000)/60)

    @staticmethod
    def get_cs_per_minute(participant: object, game_duration) -> float:
        """ Gets the cs per minute for a player based on their minions earned.

            Args:
                participant: A participant object from riot.
                game_duration: The length of the game in milliseconds.

            Returns:
                The cs per minute for a player, for this match.

        """
        return participant['totalMinionsKilled'] / ((game_duration/1000)/60)

    @staticmethod
    def get_xp_per_minute(participant: object, game_duration) -> float:
        """ Gets the xp per minute for a player based on their gold earned.

            Args:
                participant: A participant object from riot.
                game_duration: The length of the game in milliseconds.

            Returns:
                The xp per minute for a player, for this match.

        """
        return participant['champExperience'] / ((game_duration/1000)/60)


    @staticmethod
    def get_role(participant: dict) -> str:
        """ Gets a players role

            Args:
                participant: a participants stats

            Returns:
                The role the player queue'd for.

        """

        role = participant['teamPosition']
        if role == "UTILITY":
            role = "SUPPORT"

        if role == "":
            return "NONE"

        return role

    @staticmethod
    def get_enemy_champ(role: str, p_index: int, participants: dict) -> Tuple[int, str]:
        """ Gets the lane opponents champion for a player.

            Args:
                role: a string denoting our role. TOP, JUNGLE, BOTTOM, etc.
                p_index: the index of our participant dict
                participants: A large dictionary of the games participants, whos keys are ints

            Returns:
                A tuple containing the id and name of the champion that was played by our lane
                opponent.

        """

        # Support is classified as UTILITY now.
        if role == "SUPPORT":
            role = "UTILITY"

        our_team_id = participants[p_index]['teamId']

        for participant in participants:
            if participant['teamId'] != our_team_id and participant['teamPosition'] == role:
                return participant['championId'], participant['championName']

        return -1, ""

    @staticmethod
    def get_start_time_and_duration(game_create_time: float, game_duration: float) -> Tuple:
        """ Gets the start time and duration of an individual match

            Args:
                game_create_time: a float value of the game creation time
                game_duration: a float value of the game duration

            Returns:
                A Tuple containing the start_time and duration converted from MS
        """
        start_t = game_create_time

        # Creation includes miliseconds which we don't care about.
        start_t = start_t / 1000
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_t))

        # Duration might go over an hour, so I have to use a check for presentability's sake
        if game_duration >= 3600:
            duration = time.strftime("%H:%M:%S", time.gmtime(game_duration))
        else:
            duration = time.strftime("%M:%S", time.gmtime(game_duration))

        return start_time, duration

    def get_champ_name(self, champ_id: int) -> str:
        """ Gets the champ name from the champions table using their champ_id

            Args:
                champ_id: The integer value of the champion we're getting the name of

            Returns:
                The champions name, or None, if the passed champ_id was -1 (no champ)

        """

        champion_row = self.our_db.session.query(Champions).filter_by(key=champ_id).first()

        if champion_row.key != -1:
            return champion_row.name

        return "None"

    def get_allies_and_enemies(self, team_id: int, participants: list) -> Tuple[str, str]:
        """ Creates a list of allied and enemy champs played in a particular match.

            Args:
                team_id: An integer denoting what team we were on (100 or 200)
                participants: A list of participant objects from riot api

            Returns:
                A tuple containing all of the allied and enemy champions.

        """
        allies = ""
        enemies = ""
        for participant in participants:
            if participant['teamId'] == team_id:
                allies += "{}, ".format(self.get_champ_name(participant['championId']))
            else:
                enemies += "{}, ".format(self.get_champ_name(participant['championId']))

        allies = allies[:-2]
        enemies = enemies[:-2]

        return allies, enemies

    def get_team_bans(self, bans: list) -> str:
        """ Builds a list of a teams banned champions using that teams ban list

            Args:
                bans: a list containing ban dicts

            Returns:
                A string containing all of the banned champions for a team
        """
        list_of_bans = ""

        for ban in bans:
            list_of_bans += "{}, ".format(self.get_champ_name(ban['championId']))

        list_of_bans = list_of_bans[:-2]
        return list_of_bans

    def get_items(self, participant_stats: dict) -> str:
        """ Builds a string containing all of the items purchased by a participant

            Args:
                participant_stats: a dictionary containing all of a participants stats

            Returns:
                A string of item names
        """
        champ_items = ""
        items = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']

        for item in items:

            # Riot returns 'no item' as 0. So if it's 0, skip getting this item.
            if participant_stats[item] == 0:
                continue

            items_row = self.our_db.session.query(Items)\
                    .filter_by(key=participant_stats[item]).first()

            if items_row:
                champ_items += "{}, ".format(items_row.name)
            else:
                champ_items += "NOT FOUND, " # I may eventually only return slots with items

        champ_items = champ_items[:-2]

        return champ_items

    @staticmethod
    def get_perks(participant_stats: dict) -> str:
        """ This function creates a string of perk ids. TODO: Get perk name from db when we can.

            Args:
                participant_stats: A dict from riot games containing stats info

            Returns:
                A string of perk ids
        """
        champ_perks = ""
        perks = ['perk0', 'perk1', 'perk2', 'perk3', 'perk4', 'perk5']
        for perk in perks:
            if perk in participant_stats:
                champ_perks += f"{participant_stats[perk]}, "

        champ_perks = champ_perks[:-2]
        return champ_perks

    def get_team_data(self, match_data: dict, account_id: str) -> Tuple[Dict, Dict, int]:
        """ Returns Team data for both teams, as well as the team_id for both teams

            Args:
                match_data: A dict containing lots of data about our match
                account_id: the account id of the player we're getting the team data of

            Returns:
                team_data: our teams data from this match
                enemy_team-data: enemy teams data from this match
                team_id: our teams team_id
        """

        match_data = match_data['info']

        participant_index = self.get_participant_index(match_data['participants'],\
                account_id)

        participant = match_data['participants'][participant_index]

        team_id = participant['teamId']

        if team_id == 100:
            team_data = match_data['teams'][0]
            enemy_team_data = match_data['teams'][1]
        elif team_id == 200:
            team_data = match_data['teams'][1]
            enemy_team_data = match_data['teams'][0]

        return team_data, enemy_team_data, team_id


    @staticmethod
    def get_first_blood_kill_assist(stats: dict) -> Tuple[int, int]:
        """ Returns integers denoting if a participant was involved in a first blood. If a
            participant was not involved, these keys do not exist.

            Args:
                stats: a large dictionary object containing a ton of stats

            Returns:
                Two integers denoting if this participant was (1) or was not (0) part of fb

        """

        if 'firstBloodKill' in stats:
            first_blood_kill = stats['firstBloodKill']
        else:
            first_blood_kill = 0

        if 'firstBloodAssist' in stats:
            first_blood_assist = stats['firstBloodAssist']
        else:
            first_blood_assist = 0

        return int(first_blood_kill), int(first_blood_assist)

    def get_account_id(self, account_name: str) -> str:
        """ Gets the account ID we have for this username that we have stored in the league
            users table.

            Args:
                account_name: the account name we're getting the puuid for

            Returns:
                The puuid associated with this account from the database.
        """

        user_row  = self.our_db.session.query(LeagueUsers).filter_by(\
                summoner_name=account_name).first()

        return user_row.puuid

    def store_puuid(self, account_name: str, puuid: str):
        """ Stores a puuid into an league user row for a particiular account_name

            Args:
                account_name: the account name we're storing the puuid for
                puuid:        the puuid we're storing.

        """
        league_user = self.our_db.session.query(LeagueUsers).filter_by(\
                summoner_name=account_name).first()

        league_user.puuid = puuid

        self.our_db.session.commit()

    def store_league_user(self, account_data):
        """ Stores a puuid into an league user row for a particiular account_name

            Args:
                account_data: Account data from riot games

        """
        league_user = LeagueUsers()

        league_user.puuid = account_data['puuid']
        league_user.summoner_name = account_data['name']
        league_user.riot_id = account_data['accountId']

        self.our_db.session.add(league_user)
        self.our_db.session.commit()
