import json
from django.core.management.base import BaseCommand
from django.db import transaction
from lolData.models import MatchData, JsonData, Items


class Command(BaseCommand):
    help = "Corrects 'NOT FOUND' items in match_data by looking up item IDs in json_data."

    def handle(self, *args, **options):
        matches = (
            MatchData.objects
            .filter(items__icontains="NOT FOUND")
            .values_list("match_id", "player", "id")
        )

        match_count = matches.count()
        self.stdout.write(self.style.NOTICE(f"Found {match_count} matches to fix."))

        progress = 1
        for match_id, summoner_name, record_id in matches:
            item_list = self.get_items_from_json(match_id, summoner_name)
            if not item_list:
                continue

            new_item_string = self.get_item_names(item_list)

            self.stdout.write(
                f"{progress} of {match_count}. "
                f"Adding '{new_item_string}' to match {match_id} (record {record_id})"
            )
            self.update_record(new_item_string, record_id)
            progress += 1

        self.stdout.write(self.style.SUCCESS("All matches processed."))

    def get_items_from_json(self, match_id, summoner):
        """Get item IDs for the given match and summoner from json_data."""
        json_row = JsonData.objects.filter(match_id=match_id).first()
        if not json_row:
            self.stdout.write(self.style.WARNING(f"No JSON data for {match_id}, skipping."))
            return None

        data = json.loads(json_row.json_data)
        participant_id = next(
            (p["participantId"] for p in data["participantIdentities"]
             if p["player"]["summonerName"].lower() == summoner.lower()),
            None
        )
        if not participant_id:
            return None

        for participant in data["participants"]:
            if participant["participantId"] == participant_id:
                return [
                    participant["stats"]["item0"],
                    participant["stats"]["item1"],
                    participant["stats"]["item2"],
                    participant["stats"]["item3"],
                    participant["stats"]["item4"],
                    participant["stats"]["item5"],
                    participant["stats"]["item6"],
                ]
        return None

    def get_item_names(self, items):
        """Look up item names for the given list of item IDs."""
        names = []
        for item_id in items:
            if item_id == 0:
                continue
            item = Items.objects.filter(key=item_id).first()
            if item:
                names.append(item.name)
        return ", ".join(names).replace("'", "''")

    @transaction.atomic
    def update_record(self, item_string, record_id):
        """Update the match_data record's items field."""
        MatchData.objects.filter(id=record_id).update(items=item_string)
