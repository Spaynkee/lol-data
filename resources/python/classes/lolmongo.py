""" lolmongo.py class

This class has all the objects and properties we need to interact with our mongodb. This should
only be used in lolparser.py and in scripts as needed.

"""

import pymongo

#pylint: disable=too-many-instance-attributes # This should be fine for lolmongo.
#pylint: disable=too-few-public-methods # also fine for lolmongo.
#pylint: disable=C0103 # TOODO: change self.db and its references to have a longer name
class LolMongo():
    """ Contains all the methods and functions needed by lolmongo.py and lolaccount.py
        Attributes:

    """

    def __init__(self, host, user, pw, name=''):
        mongodb_conn = pymongo.MongoClient(f"mongodb://{user}:{pw}@{host}")
        self.db = mongodb_conn[name]

        self.json = self.db.json
        self.timeline_json = self.db.timeline_json
