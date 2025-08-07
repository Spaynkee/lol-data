import json
import os
import pytest
from lolData.management.helpers.lolparser import LolParser
from lolData.models import MatchData  # adjust to your actual model name

@pytest.mark.django_db
def test_team_data_inserted():
    # Get absolute path relative to this test file:
    test_file_path = os.path.join(os.path.dirname(__file__), '..', 'test_statics', '1')
    test_file_path = os.path.abspath(test_file_path)

    with open(test_file_path, 'r') as test_file:
        match_dict = json.load(test_file)

    parser = LolParser()

    # Mock internal methods if needed (e.g. participant index):
    parser.get_participant_index = lambda *args, **kwargs: 2

    # Call your method, which should save to DB via Django ORM
    parser.insert_match_data_row(match_dict, "Spaynkee",
                                 "OIesQl3aYp9Mlfi7OgKFXp1i2brmVO0QUMSE0adgol7L2g")

    # Now query the database for the saved row:
    match_data_obj = MatchData.objects.filter(player="Spaynkee", match_id=4251366296).first()
    assert match_data_obj is not None

    assert match_data_obj.role == "MIDDLE"
    assert match_data_obj.champion == 245
    assert match_data_obj.first_blood == 1
    assert match_data_obj.first_blood_assist == 0
    assert match_data_obj.kills == 14
    assert match_data_obj.deaths == 12
    assert match_data_obj.assists == 7
    assert match_data_obj.damage_to_champs == 24382
    assert match_data_obj.damage_to_turrets == 2140
    assert abs(match_data_obj.gold_per_minute - 493.32589285714284) < 0.001
    assert abs(match_data_obj.creeps_per_minute - 5.189732142857142) < 0.001
    assert abs(match_data_obj.xp_per_minute - 562.9017857142857) < 0.001
    assert match_data_obj.wards_placed == 11
    assert match_data_obj.vision_wards_bought == 1
    assert match_data_obj.wards_killed == 2
