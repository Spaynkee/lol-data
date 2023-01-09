""" test_lolparser.py

This test suite contains all currently written unit tests for the lolparser.py class.

There is one class for every lolparser function, so new test cases should be added as functions
belonging to the classes in this file.


Don't forget -- Run this from the root folder /lol-data and use the command
python -m unittest resources.python.test.unit.test_lolparser

"""
#pylint: disable=import-error # False positive.
#pylint: disable=no-self-use # Gotta keep self for unittest
#pylint: disable=duplicate-code # They're tests, it's fine
import unittest
from unittest.mock import Mock, MagicMock
from resources.python.classes.lolparser import LolParser

class TestLolParserGetFirstBloodKillAssist(unittest.TestCase):
    """ Contains all the test cases for get_first_blood_kill_assist().
    """

    def test_with_zeros(self):
        """ Tests with 0's as inputs.
        """

        data = {'firstBloodKill': 0, 'firstBloodAssist': 0}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_empty_dict(self):
        """ tests with an empty dictionary as input.
        """

        data = {}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (0, 0))

    def test_with_ones(self):
        """ tests with 1's as inputs.
        """

        data = {'firstBloodKill': 1, 'firstBloodAssist': 1}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 1))

    def test_with_strings(self):
        """ tests passing strings as the value of the key. This shouldn't happen,
            but we should make sure our function still works if it does.
        """

        data = {'firstBloodKill': '1', 'firstBloodAssist': '0'}
        result = LolParser.get_first_blood_kill_assist(data)

        self.assertEqual(result, (1, 0))

class TestLolParserGetPerks(unittest.TestCase):
    """ Contains all the test cases for get_perks().
    """
    def test_get_perks(self):
        """ tests with standard inputs
        """

        data = {"perk0": "0", "perk1": "1", "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = LolParser.get_perks(data)

        self.assertEqual(result, "0, 1, 2, 3, 4, 5")

    def test_get_perks_with_missing_perks(self):
        """ tests with a missing perk. This shouldn't happen, but if it does it should be
            handeled.
        """

        data = {"perk0": "0",  "perk2": "2", "perk3": "3", "perk4": "4", "perk5": "5"}
        result = LolParser.get_perks(data)

        self.assertEqual(result, "0, 2, 3, 4, 5")

class TestLolParserGetStartTimeAndDuration(unittest.TestCase):
    """ Contains all the test cases for get_start_time_and_duration().
    """
    def test_with_sub_hour_duration(self):
        """ tests with a duration of less than 60 minutes.
        """
        create_time = 1527560127149
        duration = 3599
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "59:59"))

    def test_with_exactly_one_hour_duration(self):
        """ tests with a duration of exactly 60 minutes.
        """
        create_time = 1527560127149
        duration = 3600
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:00:00"))

    def test_with_super_hour_duration(self):
        """ tests with a duration greater than 60 minutes
        """
        create_time = 1527560127149
        duration = 3660
        result = LolParser.get_start_time_and_duration(create_time, duration)

        self.assertEqual(result, ("2018-05-28 21:15:27", "01:01:00"))

class TestLolParserSelectPreviousTeamDataRows(unittest.TestCase):
    """ Contains all the test cases for select_previous_team_data_rows
    """

    @staticmethod
    def test_function_calls():
        """ Asserts that query() and all() get called exactly once."""

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        parser.select_previous_team_data_rows()

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().all.assert_called_once()

class TestLolParserSelectPreviousMatchDataRows(unittest.TestCase):
    """ Contains all the test cases for select_previous_match_data_rows
    """

    @staticmethod
    def test_function_calls():
        """ Asserts that query(), all(), and filter_by() get called exactly once."""

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        parser.select_previous_match_data_rows(Mock())

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().filter_by.assert_called_once()
        mock_db_class.session.query().filter_by().all.assert_called_once()

class TestLolParserGetPreviousTeamDataMatchIds(unittest.TestCase):
    """ Contains all the test cases for get_previous_team_data_match_ids
    """

    def test_with_match_ids(self):
        """ If given a list of objects match_ids, a list of ints gets returned """

        mock_select_previous_team_data = MagicMock()
        mock_previous_team_data = []

        mock_first_row = Mock()
        mock_first_row.match_id = 111
        mock_previous_team_data.append(mock_first_row)

        mock_second_row = Mock()
        mock_second_row.match_id = 222
        mock_previous_team_data.append(mock_second_row)

        mock_third_row = Mock()
        mock_third_row.match_id = 333
        mock_previous_team_data.append(mock_third_row)

        mock_select_previous_team_data.return_value = mock_previous_team_data

        parser = LolParser()
        parser.select_previous_team_data_rows = mock_select_previous_team_data

        result = parser.get_previous_team_data_match_ids()
        mock_select_previous_team_data.assert_called_once()
        self.assertEqual(result, [111, 222, 333])
        self.assertEqual(type(result[0]), int)

class TestLolParserGetPreviousPlayerMatchDataIds(unittest.TestCase):
    """ Contains all the test cases for get_previous_player_match_data_ids
    """

    def test_with_ids(self):
        """ If given a list of objects match_ids, a list of ints gets returned """

        mock_select_previous_match_data_rows = MagicMock()
        mock_previous_match_data = []

        mock_first_row = Mock()
        mock_first_row.match_id = 111
        mock_previous_match_data.append(mock_first_row)

        mock_second_row = Mock()
        mock_second_row.match_id = 222
        mock_previous_match_data.append(mock_second_row)

        mock_third_row = Mock()
        mock_third_row.match_id = 333
        mock_previous_match_data.append(mock_third_row)

        mock_select_previous_match_data_rows.return_value = mock_previous_match_data

        parser = LolParser()
        parser.select_previous_match_data_rows = mock_select_previous_match_data_rows

        result = parser.get_previous_player_match_data_ids(Mock())
        mock_select_previous_match_data_rows.assert_called_once()

        self.assertEqual(result, [111, 222, 333])
        self.assertEqual(type(result[0]), int)

class TestLolParserInsertMatchDataRow(unittest.TestCase):
    """ Contains all the test cases for insert_match_data_row
    """

    def test_number_of_function_calls(self):
        """ tests that the number of functions called is exactly what we expected."""

        mock_dict = MagicMock()
        mock_db = MagicMock()

        # mock function calls.
        mock_get_participant_index = MagicMock()
        mock_get_champ_name = MagicMock()
        mock_get_first_blood_kill_assist = MagicMock(return_value=[None,None])
        mock_get_role = MagicMock()
        mock_get_perks = MagicMock()
        mock_get_items = MagicMock()
        mock_get_enemy_champ = MagicMock(return_value=[None,None])
        mock_get_gold_per_minute = MagicMock()
        mock_get_cs_per_minute = MagicMock()
        mock_get_xp_per_minute = MagicMock()

        parser = LolParser()

        parser.our_db = mock_db
        parser.get_participant_index = mock_get_participant_index
        parser.get_champ_name = mock_get_champ_name
        parser.get_first_blood_kill_assist = mock_get_first_blood_kill_assist
        parser.get_role = mock_get_role
        parser.get_enemy_champ = mock_get_enemy_champ
        parser.get_perks = mock_get_perks
        parser.get_items = mock_get_items
        parser.get_enemy_champ = mock_get_enemy_champ
        parser.get_gold_per_minute = mock_get_gold_per_minute
        parser.get_cs_per_minute = mock_get_cs_per_minute
        parser.get_xp_per_minute = mock_get_xp_per_minute

        parser.insert_match_data_row(mock_dict, "test", Mock())

        # make sure our functions are called the correct number of times.
        mock_db.session.add.assert_called_once()
        mock_get_participant_index.assert_called_once()
        mock_get_champ_name.assert_called_once()
        mock_get_first_blood_kill_assist.assert_called_once()
        mock_get_role.assert_called_once()
        mock_get_enemy_champ.assert_called_once()
        mock_get_perks.assert_called_once()
        mock_get_items.assert_called_once()
        mock_get_enemy_champ.assert_called_once()
        mock_get_gold_per_minute.assert_called_once()
        mock_get_cs_per_minute.assert_called_once()
        mock_get_xp_per_minute.assert_called_once()



class TestLolParserInsertTeamDataRow(unittest.TestCase):
    """ Contains all the test cases for insert_team_data_row
    """

    def test_number_of_function_calls(self):
        """ tests that the number of functions called is exactly what we expected."""
        mock_dict = MagicMock()
        mock_db = MagicMock()

        # mock function calls.
        mock_get_team_data = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_get_team_bans = MagicMock()
        mock_get_allies_and_enemies = MagicMock(return_value=[None, None])
        mock_get_start_time_and_duration = MagicMock(return_value=[None, None])


        parser = LolParser()

        parser.our_db = mock_db
        parser.get_team_data = mock_get_team_data
        parser.get_team_bans = mock_get_team_bans
        parser.get_allies_and_enemies = mock_get_allies_and_enemies
        parser.get_start_time_and_duration = mock_get_start_time_and_duration

        parser.insert_team_data_row(mock_dict, "test", Mock())

        mock_db.session.add.assert_called_once()
        mock_get_team_data.assert_called_once()
        self.assertEqual(mock_get_team_bans.call_count, 2)
        mock_get_allies_and_enemies.assert_called_once()
        mock_get_start_time_and_duration.assert_called_once()

class TestLolParserStorePuuid(unittest.TestCase):
    """ Contains all the test cases for store_puuid
    """

    @staticmethod
    def test_store_puuid():
        """ Asserts that a puuid is stored. """

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        parser.store_puuid(Mock(), Mock())

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().filter_by.assert_called_once()
        mock_db_class.session.query().filter_by().first.assert_called_once()
        mock_db_class.session.commit.assert_called_once()

class TestLolParserGetAccountId(unittest.TestCase):
    """ Contains all the test cases for get_account_id
    """

    @staticmethod
    def test_get_account_id():
        """ Tests getting an account id out of the database."""

        mock_db_class = MagicMock()

        parser = LolParser()
        parser.our_db = mock_db_class

        parser.get_account_id(Mock())

        mock_db_class.session.query.assert_called_once()
        mock_db_class.session.query().filter_by.assert_called_once()
        mock_db_class.session.query().filter_by().first.assert_called_once()

if __name__ == "__main__":
    unittest.main()
