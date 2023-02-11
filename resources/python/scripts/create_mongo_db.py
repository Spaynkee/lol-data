from pymongo import MongoClient
from classes.lolconfig import LolConfig

def main():
    config = LolConfig()

    client = MongoClient(f"mongodb://{config.mongo_host}/")
    db = client.admin
    db.command("createUser", config.mongo_user, pwd=config.mongo_password, roles=["readWrite",\
            "dbAdmin"])

if __name__ == "__main__":
    main()
