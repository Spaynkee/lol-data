
import json
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from lolData.models import Champions, Items


class Command(BaseCommand):
    help = "Fetches and stores the latest champion and item data from Riot's Data Dragon API."

    def handle(self, *args, **options):
        """Main entry point for the management command."""
        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        version_res = requests.get(version_url)
        versions = json.loads(version_res.text)

        latest_version = versions[0]

        self.stdout.write(self.style.SUCCESS(f"Updating static data for patch {latest_version}"))

        self.store_champion_data([latest_version])
        self.store_item_data([latest_version])
        # self.store_item_data(versions)  # Uncomment if you want all historical items

        self.stdout.write(self.style.SUCCESS("Static data update complete."))

    @transaction.atomic
    def store_champion_data(self, versions: list):
        """Fetch and store champion data."""
        for version in versions:
            self.stdout.write(f"Getting champion data for patch {version}")
            champs_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
            res = requests.get(champs_url)
            champ_res = json.loads(res.text)
            champ_data = champ_res['data']

            for champ in champ_data.values():
                key = champ['key']

                if Champions.objects.filter(key=key).exists():
                    continue

                Champions.objects.create(
                    key=key,
                    id=champ['id'],
                    name=champ['name'],
                    title=champ['title'],
                    blurb=champ['blurb']
                )

    @transaction.atomic
    def store_item_data(self, versions: list):
        """Fetch and store item data."""
        for version in versions:
            self.stdout.write(f"Getting item data for patch {version}")
            items_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
            res = requests.get(items_url)
            item_res = json.loads(res.text)
            item_data = item_res['data']

            for key, details in item_data.items():
                if Items.objects.filter(key=key).exists():
                    continue

                Items.objects.create(
                    key=key,
                    name=details['name']
                )
