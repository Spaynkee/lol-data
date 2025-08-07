""" update_static_data.py

    This script hits a few public apis containing data for specific patches of league of legends
    In particular, this script gets champion and item data.

"""

import json
import requests
import os
import django
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lolData.settings')
django.setup()

from classes.lolconfig import LolConfig
from lolData.models import Champions, Items

#pylint: disable=C0103 # columns are named id, which makes the linter angry.
#pylint: disable=W0622 # columns are named id, which makes the linter angry.
def main():
    """ main function of update_static_data.py

        This functions gets the latest patches static data and stores it into the db.
        By default, it should only run for the latest patch.

        It's possible to get data for multiple patches if you create a versions list
        and pass that to the functions as well.

        ex: ["3.11.2", "3.9.4","3.12.37"] etc.

    """

    config = LolConfig()

    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    version_res = requests.get(version_url)
    versions = json.loads(version_res.text)

    latest_version = versions[0]

    store_champion_data([latest_version])
    store_item_data([latest_version])
    #store_item_data(versions) # If you want every item ever.


@transaction.atomic
def store_champion_data(versions: list):
    """ Gets and processes json data about champions from riot games.

        Args:
            versions: a list of versions we're getting data for. This is usually the latest version

    """
    for version in versions:
        print(f"Getting champion data for patch {version}")
        champs_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        res = requests.get(champs_url)
        champ_res = json.loads(res.text)
        champ_data = champ_res['data']


        for champ in champ_data:
            key = champ_res['data'][champ]['key']

            champ_check = Champions.objects.filter(key=key).first()
            if champ_check:
                # Champion is already in the table, so we can skip it.
                continue

            id = champ_res['data'][champ]['id']
            name = champ_res['data'][champ]['name']
            title = champ_res['data'][champ]['title']
            blurb = champ_res['data'][champ]['blurb']

            Champions.objects.create(
                key=key,
                id=id,
                name=name,
                title=title,
                blurb=blurb
            )

@transaction.atomic
def store_item_data(versions: list):
    """ Gets and processes json data about items from riot games.

        Args:
            versions: a list of versions we're getting data for. This is usually the latest version

    """
    for version in versions:
        print(f"Getting item data for patch {version}")
        items_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
        res = requests.get(items_url)
        item_res = json.loads(res.text)
        item_data = item_res['data']

        for item in item_data:
            item_check = Items.objects.filter(key=item).first()
            if item_check:
                continue

            Items.objects.create(
                key=item,
                name=item_res['data'][item]['name']
            )

if __name__ == "__main__":
    main()