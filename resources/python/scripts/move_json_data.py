from classes.lolconfig import LolConfig
from classes.loldb import LolDB
from classes.models import LeagueUsers
from classes.lolgather import LolGather
from classes.lolparser import LolParser
from classes.lolmongo import LolMongo
from classes.models import TeamData, MatchData, JsonData, Champions, Items, ScriptRuns, LeagueUsers,\
        JsonTimeline

class MoveJson():
    def __init__(self):
        self.config = LolConfig()
        self.gather = LolGather()
        self.parser = LolParser()

        self.our_db = LolDB(self.config.db_host, self.config.db_user, self.config.db_pw,\
                self.config.db_name)

        self.mongodb = LolMongo(self.config.mongo_host, self.config.mongo_user,\
                self.config.mongo_pw, self.config.mongo_name)


    def run(self):
        """ gets all of our json, then stores it all into mongo.

        """

        json_data = self.our_db.session.query(JsonData).all()

        for row in json_data:
            print(f"storing {row.match_id} json into mongo")
            a_dict = {'_id': row.match_id,
                    'json_data': row.json_data}
            # check if exists
            if not self.mongodb.json.find_one(row.match_id):
                self.mongodb.json.insert_one(a_dict)
            else:
                continue

        timeline_data = self.our_db.session.query(JsonTimeline).all()
        for timeline in timeline_data:
            print(f"storing {timeline.match_id} timeline_json into mongo")
            a_dict = {'_id': timeline.match_id,
                    'json_timeline': timeline.json_timeline}

            if not self.mongodb.timeline_json.find_one(row.match_id):
                self.mongodb.timeline_json.insert_one(a_dict)
            else:
                continue

if __name__ == "__main__":
    move = MoveJson()
    move.run()


