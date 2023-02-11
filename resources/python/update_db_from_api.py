""" update_db_from_api.py

This script will populate the all of the tables in the db
specified in the config file.

The new data comes from the public api endpoints I have set up for these tables.
This is useful if we're creating a new test database, or if we want to copy the
data to anywhere that doesn't have access to a sql dump.

"""
import sys
import json
import requests
#pylint: disable=import-error # False positives
from classes.loldb import LolDB
from classes.lolmongo import LolMongo
from classes.lolconfig import LolConfig
from classes.models import TeamData, MatchData, ScriptRuns, Champions, Items, JsonData,\
        LeagueUsers, TimelineJsonData

#pylint: disable=too-many-locals # This is okay.
#pylint: disable=W0104 # Dropping a collection isn't a useless statement.
#pylint: disable=unreachable # safeguard from running in prod.
#pylint: disable=too-many-statements # This is also okay.
def main():
    """
        We make at least 7 requests to our public endpoints, and populate the db with that data.

    """

    # we need to drop all the existing tables so we can re populate.
    config = LolConfig()
    our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)
    our_mongo = LolMongo(config.mongo_host, config.mongo_user, config.mongo_pw, config.mongo_name)

    for collection in our_mongo.db.list_collection_names():
        our_mongo.db.drop[collection]

    our_db.metadata.drop_all(our_db.engine)
    our_db.session.commit()

    our_db.metadata.create_all(our_db.engine)
    our_db.session.commit()

    print("Getting script runs")
    # script runs table.
    my_script_run_data = requests.get("http://paulzplace.asuscomm.com/api/get_script_runs",\
            timeout=200)
    script_runs = json.loads(my_script_run_data.text)
    our_db.session.add_all([ScriptRuns(**run) for run in script_runs])

    print("getting team data")
    # team data table
    my_team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data", timeout=200)
    matches = json.loads(my_team_data.text)
    our_db.session.add_all([TeamData(**match) for match in matches])

    print("getting user data")
    # match data table
    users = ['Spaynkee', 'Dumat', 'Archemlis', 'Stylus Crude', 'dantheninja6156', 'Csqward']
    for user in users:
        user_data = get_player_data(user)
        our_db.session.add_all([MatchData(**match) for match in remove_win(user_data)])

    print("getting league users")
    #league_users table
    my_league_user_data = requests.get("http://paulzplace.asuscomm.com/api/get_league_users",\
            timeout=200)
    league_users = json.loads(my_league_user_data.text)
    our_db.session.add_all([LeagueUsers(**user) for user in league_users])

    print("getting champions")
    #champions table
    my_champion_data = requests.get("http://paulzplace.asuscomm.com/api/get_champions", timeout=200)
    champions = json.loads(my_champion_data.text)
    our_db.session.add_all([Champions(**champ) for champ in champions])

    print("getting items")
    # items table
    my_item_data = requests.get("http://paulzplace.asuscomm.com/api/get_items", timeout=200)
    items = json.loads(my_item_data.text)
    our_db.session.add_all([Items(**item) for item in items])

    print("getting json data. Big Oof")
    my_json_data_data = requests.get("http://paulzplace.asuscomm.com/api/get_json_data",\
            timeout=200)
    json_data = json.loads(my_json_data_data.text)

    for row in json_data:
        if not our_mongo.json.find_one(row['match_id']):
            a_dict = {'_id': row.match_id,
                    'json_data': row.json_data}
            our_mongo.json.insert_one(a_dict)
        else:
            continue

    print("getting timeline json data. Biggest Oof")
    my_timeline_json_data = requests.get(\
            "http://paulzplace.asuscomm.com/api/get_timeline_json_data", timeout=400)
    timeline_json_data = json.loads(my_timeline_json_data.text)

    for row in timeline_json_data:
        if not our_mongo.timeline_json.find_one(row['match_id']):
            a_dict = {'_id': row.match_id,
                    'json_data': row.json_data}
            our_mongo.timeline_json.insert_one(a_dict)
        else:
            continue

    # cut these after we drop json from sql
    our_db.session.add_all([JsonData(**json) for json in json_data])
    our_db.session.add_all([TimelineJsonData(**json) for json in timeline_json_data])
    our_db.session.commit()

def remove_win(user_data_list):
    """ our get_player_data api endpoint returns a 'win' value for ease of use, but this doesn't
        play nicely with our model set up, as we have to include 'win' as a match_data
        module param (which isn't used)

        This function removes the win column from the json data we get back so we can use
        add_all

        Args:
            user_data_list (list): a list of all of a players games

        Returns:
            an updated list of all of a players games.

    """
    for game in user_data_list:
        del game['win']

    return user_data_list


def get_player_data(player: str) -> list:
    """
        Gets an individual players data from the public api.

        Args:
            player (str): the name of the players data we're returning

        Returns:
            an array containing every row for our user in the match_data table.

    """
    return json.loads(requests.get(\
            f"http://paulzplace.asuscomm.com/api/get_user_data?name={player}", timeout=200).text)

if __name__ == "__main__":
    # If you're gonna remove this exit, you better be in test. or else.
    sys.exit()
    main()
