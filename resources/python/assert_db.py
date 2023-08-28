""" assert_db.py

Contains a class that inherits from unittest. This classes function is to assert that the data we
get back from our public apis matches exactly what is in our test database.

This is part of an 'e2e' 'test' that verifies that loldata.py gets the same exact data in test,
as it does in prod.

This step of the e2e test happens last, after the script has ran again.

"""
import sys
import json
import unittest
import requests
#pylint: disable=import-error # False positives
from classes.loldb import LolDB
from classes.lolmongo import LolMongo
from classes.lolconfig import LolConfig
from classes.models import TeamData, MatchData, ScriptRuns

#pylint: disable=too-many-locals # This is okay.
#pylint: disable=too-many-statements # This is also okay.
#pylint: disable=unreachable # we don't want this script run in prod.
#pylint: disable=unnecessary-list-index-lookup # We do need this.
class E2e(unittest.TestCase):
    """ Ensures the loldata.py script works exactly as it does in current prod.
        this script compares the data stored in prod with the data stored in test.
        They should be exactly the same if the collection script is still working exactly as it was.

    """
    def test(self):
        """ This function does the prod/test comparison.

        """
        config = LolConfig()

        our_db = LolDB(config.db_host, config.db_user, config.db_pw, config.db_name)
        our_mongo = LolMongo(config.mongo_host, config.mongo_user, config.mongo_pw,\
                config.mongo_name)

        # get team data from prod
        my_team_data = requests.get("http://paulzplace.asuscomm.com/api/get_team_data", timeout=200)
        prod_team_data = json.loads(my_team_data.text)

        # get team data from test
        test_team_data = our_db.session.query(TeamData).order_by(TeamData.match_id.desc()).all()

        self.assertEqual(len(prod_team_data), len(test_team_data))

        print("Checking team_data")
        for i, _ in enumerate(prod_team_data):
            self.assertEqual(prod_team_data[i]['match_id'], test_team_data[i].match_id)
            self.assertEqual(str(prod_team_data[i]['game_version']),\
                    str(test_team_data[i].game_version))
            self.assertEqual(prod_team_data[i]['win'], str(test_team_data[i].win))
            self.assertEqual(prod_team_data[i]['participants'], str(test_team_data[i].participants))
            self.assertEqual(prod_team_data[i]['first_blood'], str(test_team_data[i].first_blood))
            self.assertEqual(prod_team_data[i]['first_baron'], str(test_team_data[i].first_baron))
            self.assertEqual(prod_team_data[i]['first_tower'], str(test_team_data[i].first_tower))
            self.assertEqual(prod_team_data[i]['first_dragon'], str(test_team_data[i].first_dragon))
            self.assertEqual(str(prod_team_data[i]['first_inhib']),\
                    str(test_team_data[i].first_inhib))
            self.assertEqual(str(prod_team_data[i]['first_rift_herald']),\
                    str(test_team_data[i].first_rift_herald))
            self.assertEqual(str(prod_team_data[i]['ally_dragon_kills']),\
                    str(test_team_data[i].ally_dragon_kills))
            self.assertEqual(str(prod_team_data[i]['ally_rift_herald_kills']),\
                    str(test_team_data[i].ally_rift_herald_kills))

            self.assertEqual(str(prod_team_data[i]['enemy_dragon_kills']),\
                    str(test_team_data[i].enemy_dragon_kills))
            self.assertEqual(str(prod_team_data[i]['enemy_rift_herald_kills']),\
                    str(test_team_data[i].enemy_rift_herald_kills))

            self.assertEqual(str(prod_team_data[i]['inhib_kills']),\
                    str(test_team_data[i].inhib_kills))
            self.assertEqual(str(prod_team_data[i]['bans']), str(test_team_data[i].bans))
            self.assertEqual(str(prod_team_data[i]['enemy_bans']),\
                    str(test_team_data[i].enemy_bans))
            self.assertEqual(str(prod_team_data[i]['allies']), str(test_team_data[i].allies))
            self.assertEqual(str(prod_team_data[i]['enemies']), str(test_team_data[i].enemies))
            self.assertEqual(str(prod_team_data[i]['start_time']),\
                    str(test_team_data[i].start_time))


        users = ['Spaynkee', 'Dumat', 'Archemlis', 'Stylus Crude', 'dantheninja6156', 'Csqward']
        for user in users:
            print(f"Checking match_data for {user}")
            prod_user_data = json.loads(requests.get(\
                f"http://paulzplace.asuscomm.com/api/get_user_data?name={user}", timeout=200).text)

            test_user_data = our_db.session.query(MatchData).filter_by(player=user).order_by(\
                    MatchData.match_id.desc()).all()

            self.assertEqual(len(prod_user_data), len(test_user_data))

            for i, _ in enumerate(prod_user_data):
                self.assertEqual(str(prod_user_data[i]['match_id']),\
                        str(test_user_data[i].match_id))
                self.assertEqual(str(prod_user_data[i]['player']), str(test_user_data[i].player))
                self.assertEqual(str(prod_user_data[i]['role']), str(test_user_data[i].role))
                self.assertEqual(str(prod_user_data[i]['champion']),\
                        str(test_user_data[i].champion))
                self.assertEqual(str(prod_user_data[i]['champion_name']),\
                        str(test_user_data[i].champion_name))
                self.assertEqual(str(prod_user_data[i]['enemy_champion']),\
                        str(test_user_data[i].enemy_champion))

                self.assertEqual(str(prod_user_data[i]['enemy_champion_name']),\
                        str(test_user_data[i].enemy_champion_name))

                self.assertEqual(str(prod_user_data[i]['first_blood']),\
                        str(test_user_data[i].first_blood))
                self.assertEqual(str(prod_user_data[i]['first_blood_assist']),\
                        str(test_user_data[i].first_blood_assist))
                self.assertEqual(str(prod_user_data[i]['kills']), str(test_user_data[i].kills))
                self.assertEqual(str(prod_user_data[i]['assists']), str(test_user_data[i].assists))
                self.assertEqual(str(prod_user_data[i]['deaths']), str(test_user_data[i].deaths))
                self.assertEqual(str(prod_user_data[i]['damage_to_champs']),\
                        str(test_user_data[i].damage_to_champs))
                self.assertEqual(str(prod_user_data[i]['damage_to_turrets']),\
                        str(test_user_data[i].damage_to_turrets))

                # floats don't like to cooperate.
                if test_user_data[i].gold_per_minute:
                    self.assertEqual(prod_user_data[i]['gold_per_minute'],\
                            f'{float(test_user_data[i].gold_per_minute):g}')

                if test_user_data[i].creeps_per_minute:
                    self.assertEqual(prod_user_data[i]['creeps_per_minute'],\
                            f'{float(test_user_data[i].creeps_per_minute):g}')

                if test_user_data[i].xp_per_minute:
                    self.assertEqual(prod_user_data[i]['xp_per_minute'],\
                            f'{float(test_user_data[i].xp_per_minute):g}')

                self.assertEqual(str(prod_user_data[i]['wards_placed']),\
                        str(test_user_data[i].wards_placed))

                self.assertEqual(str(prod_user_data[i]['vision_wards_bought']),\
                        str(test_user_data[i].vision_wards_bought))

                self.assertEqual(str(prod_user_data[i]['wards_killed']),\
                        str(test_user_data[i].wards_killed))
                self.assertEqual(str(prod_user_data[i]['items']), str(test_user_data[i].items))
                self.assertEqual(str(prod_user_data[i]['perks']), str(test_user_data[i].perks))

        print("Checking json_data")
        my_json_data = requests.get("http://paulzplace.asuscomm.com/api/get_json_data", timeout=200)

        prod_json_data = list(json.loads(my_json_data.text))
        test_json_data = list(our_mongo.json.find().sort("_id", 1))

        self.assertEqual(len(prod_json_data), len(test_json_data))

        #TODO: Eventually I want to verify the json exactly, but that's tricky right now.

        #for i in range(-1, -21, -1):
        #    print(prod_json_data[i]['metadata']['matchId'])
        #    continue

        #    prod_id = prod_json_data[i]['metadata']['matchId']
        #    test_id = json.loads(test_json_data[i]['json_data'])['metadata']['matchId']

        #    if prod_id != test_id:
        #        self.fail(f'{prod_id} != {test_id}')
        #        return
        #    else:
        #        print(prod_id)
        #        continue

        #    self.assertEqual(prod_json_data[i],\
        #            json.loads(test_json_data[i]['json_data']))

        #return

        print("Checking timeline_data")
        my_timeline_json_data = requests.get(\
                "http://paulzplace.asuscomm.com/api/get_timeline_json_data",\
                timeout=200)

        prod_timeline_json_data = list(json.loads(my_timeline_json_data.text))
        test_timeline_json_data = list(our_mongo.timeline_json.find())

        self.assertEqual(len(prod_timeline_json_data), len(test_timeline_json_data))

        #for i in range(-21, 0):
        #    self.assertEqual(prod_timeline_json_data[i],\
        #            json.loads(test_timeline_json_data[i]['json_timeline']))

        print("Checking Script Runs")
        my_runs_data = requests.get("http://paulzplace.asuscomm.com/api/get_script_runs",\
                timeout=200)
        prod_run_data = json.loads(my_runs_data.text)
        test_run_data = our_db.session.query(ScriptRuns).all()

        # the test db will have one more script run, the one that just happened.
        self.assertEqual(len(prod_run_data)+1, len(test_run_data))

        for i, _ in enumerate(prod_run_data):
            self.assertEqual(prod_run_data[i]['id'], test_run_data[i].id)
            self.assertEqual(prod_run_data[i]['source'], test_run_data[i].source)
            self.assertEqual(prod_run_data[i]['status'], test_run_data[i].status)
            self.assertEqual(prod_run_data[i]['matches_added'], test_run_data[i].matches_added)

        # make sure our script run was recorded correctly.
        self.assertEqual(prod_run_data[-1]['id']+1, test_run_data[-1].id)
        self.assertEqual("Test", test_run_data[-1].source)
        self.assertEqual("Success", test_run_data[-1].status)

if __name__ == "__main__":
    # If you're gonna remove this exit, you better be in test. or else.
    sys.exit()
    unittest.main()
