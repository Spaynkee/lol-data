import unittest
import json
from collections import defaultdict
from unittest.mock import Mock, MagicMock
from resources.python.classes.lolparser import LolParser

# This is being ignored in the build for now, as it needs more significant changes.
class TestTeamDataInserted(unittest.TestCase):
    """ Contains all the test cases for inserting team data.
    """

    def setUp(self):
        pass

    def test_with_data(self):
        pass
        """ tests that data is parsed correctly. 
            
            This will test that we parse data out correctly, assuming we can get data from
            riot.

            This will test several things, including our parser function, all the functions in the
            parser, and storing data into the database?
        """

        test_file = open("resources/python/test/test_statics/1", "r")
        match_dict = json.loads(test_file.read())
        
        mock_db = MagicMock()
        mock_get_participant_index = MagicMock()
        mock_get_participant_index.return_value = 2

        parser = LolParser()

        parser.our_db = mock_db
        parser.get_participant_index = mock_get_participant_index

        parser.insert_match_data_row(match_dict, "Spaynkee",\
                "OIesQl3aYp9Mlfi7OgKFXp1i2brmVO0QUMSE0adgol7L2g")

        match_data_obj = mock_db.session.add.call_args.args[0]

        self.assertEqual(match_data_obj.player, "Spaynkee")
        self.assertEqual(match_data_obj.match_id, 4251366296)
        self.assertEqual(match_data_obj.role, "MIDDLE")
        self.assertEqual(match_data_obj.champion, 245)
        self.assertEqual(match_data_obj.first_blood, 1)
        self.assertEqual(match_data_obj.first_blood_assist, 0)
        self.assertEqual(match_data_obj.kills, 14)
        self.assertEqual(match_data_obj.deaths, 12)
        self.assertEqual(match_data_obj.assists, 7)
        self.assertEqual(match_data_obj.damage_to_champs, 24382)
        self.assertEqual(match_data_obj.damage_to_turrets, 2140)
        self.assertEqual(match_data_obj.gold_per_minute, 493325.89285714284)
        self.assertEqual(match_data_obj.creeps_per_minute, 5189.732142857143)
        self.assertEqual(match_data_obj.xp_per_minute, 562901.7857142857)
        self.assertEqual(match_data_obj.wards_placed, 11)
        self.assertEqual(match_data_obj.vision_wards_bought, 1)
        self.assertEqual(match_data_obj.wards_killed, 2)

        test_file.close()
