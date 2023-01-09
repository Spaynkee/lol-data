import requests
from classes.lolconfig import LolConfig
from classes.loldb import LolDB
from classes.models import LeagueUsers
from classes.lolgather import LolGather
from classes.lolparser import LolParser

class GetPuuid():
    def __init__(self):
        self.config = LolConfig()
        self.gather = LolGather()
        self.parser = LolParser()

        self.our_db = LolDB(self.config.db_host, self.config.db_user, self.config.db_pw,\
                self.config.db_name)

        self.summoner_names = self.parser.get_summoner_names()

    def run(self):
        """ gets the puuid, then stored the puuid, for each name.

        """
        for name in self.summoner_names:
            puuid = self.gather.get_puuid(name)
            self.parser.store_puuid(name, puuid)


if __name__ == "__main__":
    puuid = GetPuuid()
    puuid.run()


