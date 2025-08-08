from django.db import models


class TeamData(models.Model):
    match_id = models.BigIntegerField(primary_key=True)
    game_version = models.CharField(max_length=40, null=True, blank=True)
    win = models.CharField(max_length=10, null=True, blank=True)
    participants = models.CharField(max_length=80, null=True, blank=True)
    first_blood = models.SmallIntegerField(null=True, blank=True)
    first_baron = models.SmallIntegerField(null=True, blank=True)
    first_tower = models.SmallIntegerField(null=True, blank=True)
    first_dragon = models.SmallIntegerField(null=True, blank=True)
    first_inhib = models.SmallIntegerField(null=True, blank=True)
    first_rift_herald = models.SmallIntegerField(null=True, blank=True)
    ally_dragon_kills = models.IntegerField(null=True, blank=True)
    ally_rift_herald_kills = models.IntegerField(null=True, blank=True)
    inhib_kills = models.IntegerField(null=True, blank=True)
    bans = models.CharField(max_length=80, null=True, blank=True)
    enemy_bans = models.CharField(max_length=80, null=True, blank=True)
    allies = models.CharField(max_length=80, null=True, blank=True)
    enemies = models.CharField(max_length=80, null=True, blank=True)
    enemy_dragon_kills = models.IntegerField(null=True, blank=True)
    enemy_rift_herald_kills = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        db_table = "team_data"
        verbose_name = "Team Data"
        verbose_name_plural = "Team Data"

    def __str__(self):
        return f"Match {self.match_id} - {'Win' if self.win else 'Loss'}"


class MatchData(models.Model):
    id = models.AutoField(primary_key=True)
    match_id = models.BigIntegerField(null=True, blank=True)
    player = models.CharField(max_length=40, null=True, blank=True)
    role = models.CharField(max_length=10, null=True, blank=True)
    champion = models.IntegerField(null=True, blank=True)
    champion_name = models.CharField(max_length=40, null=True, blank=True)
    enemy_champion = models.IntegerField(null=True, blank=True)
    enemy_champion_name = models.CharField(max_length=40, null=True, blank=True)
    first_blood = models.SmallIntegerField(null=True, blank=True)
    first_blood_assist = models.SmallIntegerField(null=True, blank=True)
    kills = models.IntegerField(null=True, blank=True)
    deaths = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    damage_to_champs = models.IntegerField(null=True, blank=True)
    damage_to_turrets = models.IntegerField(null=True, blank=True)
    gold_per_minute = models.FloatField(null=True, blank=True)
    creeps_per_minute = models.FloatField(null=True, blank=True)
    xp_per_minute = models.FloatField(null=True, blank=True)
    wards_placed = models.IntegerField(null=True, blank=True)
    vision_wards_bought = models.IntegerField(null=True, blank=True)
    wards_killed = models.IntegerField(null=True, blank=True)
    items = models.CharField(max_length=200, null=True, blank=True)
    perks = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "match_data"
        verbose_name = "Match Data"
        verbose_name_plural = "Match Data"

    def __str__(self):
        return f"{self.player} - {self.champion_name} (Match {self.match_id})"


class LeagueUsers(models.Model):
    id = models.AutoField(primary_key=True)
    summoner_name = models.CharField(max_length=30, null=True, blank=True)
    riot_id = models.CharField(max_length=400, null=True, blank=True)
    puuid = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        db_table = "league_users"
        verbose_name = "League User"
        verbose_name_plural = "League Users"

    def __str__(self):
        return self.summoner_name or f"User {self.id}"


class ScriptRuns(models.Model):
    SOURCE_CHOICES = [
        ("prod", "Production"),
        ("test", "Test"),
        ("manual", "Manual"),
    ]

    STATUS_CHOICES = [
        ("success", "Success"),
        ("failure", "Failure"),
        ("running", "Running"),
    ]

    id = models.AutoField(primary_key=True)
    source = models.CharField(
        max_length=50, choices=SOURCE_CHOICES, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, null=True, blank=True
    )
    matches_added = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    message = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = "script_runs"
        verbose_name = "Script Run"
        verbose_name_plural = "Script Runs"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Script Run {self.id} - {self.status}"

    @property
    def duration(self):
        """Calculate the duration of the script run."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class JsonData(models.Model):
    """JsonData model for json_data table.

    Attributes:
        match_id: Primary Key; the match_id associated with this json_data.
        json_data: The raw json returned by riot games api.
    """

    match_id = models.BigIntegerField(primary_key=True)
    json_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "json_data"
        verbose_name = "JSON Data"
        verbose_name_plural = "JSON Data"

    def __str__(self):
        return f"JSON Data for Match {self.match_id}"


class JsonTimeline(models.Model):
    match_id = models.BigIntegerField(primary_key=True)
    json_timeline = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "json_timeline"
        verbose_name = "JSON Timeline"
        verbose_name_plural = "JSON Timelines"

    def __str__(self):
        return f"Timeline Data for Match {self.match_id}"


class Champions(models.Model):
    """Champions model for the champions table.

    Attributes:
        key: Primary Key; the integer associated with this champion.
        id: The short identifier for the champion. Ex: Nunu for Nunu & Willump
        name: The full name of the champion
        title: The flavor title for the champion Ex: The Dark Child (Annie)
        blurb: The flavor text for the champion. Their backstory.
    """

    key = models.IntegerField(primary_key=True)
    id = models.CharField(max_length=30, null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    blurb = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        db_table = "champions"
        verbose_name = "Champion"
        verbose_name_plural = "Champions"
        ordering = ["name"]

    def __str__(self):
        return self.name or f"Champion {self.key}"


class Items(models.Model):
    key = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        db_table = "items"
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["name"]

    def __str__(self):
        return self.name or f"Item {self.key}"
