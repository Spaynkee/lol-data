from django.core.management.base import BaseCommand
from lolData.models import LeagueUsers  # adjust if model lives elsewhere
from lolData.management.helpers.lolgather import LolGather  # keeping your existing logic
from django.db import transaction


class Command(BaseCommand):
    help = "Fetches PUUIDs for all LeagueUsers without one and updates the database."

    def handle(self, *args, **options):
        gather = LolGather()

        users = LeagueUsers.objects.filter(puuid__isnull=True).values_list("summoner_name", flat=True)
        total = users.count()
        self.stdout.write(self.style.NOTICE(f"Found {total} users missing PUUIDs."))

        progress = 1
        for name in users:
            puuid = gather.get_puuid(name)
            if not puuid:
                self.stdout.write(self.style.WARNING(f"Could not get PUUID for {name}, skipping."))
                continue

            self.update_user_puuid(name, puuid)

            self.stdout.write(f"{progress} of {total}: Stored PUUID for {name}")
            progress += 1

        self.stdout.write(self.style.SUCCESS("All users processed."))

    @transaction.atomic
    def update_user_puuid(self, summoner_name, puuid):
        """Updates the PUUID for a given summoner name."""
        LeagueUsers.objects.filter(summoner_name=summoner_name).update(puuid=puuid)
