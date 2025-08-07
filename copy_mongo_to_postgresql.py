from pymongo import MongoClient
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file into environment variables

def copy_mongo_to_postgres(
    mongo_collection,
    json_field_name,
    pg_table,
    pg_conn,
    id_field="match_id"
):
    pg_cursor = pg_conn.cursor()

    # Step 1: Get existing IDs from PostgreSQL
    pg_cursor.execute(f"SELECT {id_field} FROM {pg_table}")
    existing_ids = set(row[0] for row in pg_cursor.fetchall())

    # Step 2: Fetch MongoDB documents
    new_docs = []
    for doc in mongo_collection.find():
        mongo_id = int(doc["_id"])
        if mongo_id not in existing_ids:
            json_data = doc.get(json_field_name)
            if json_data is not None:
                new_docs.append((mongo_id, json.dumps(json_data)))

    # Step 3: Insert into PostgreSQL
    if new_docs:
        insert_query = f"""
            INSERT INTO {pg_table} ({id_field}, {json_field_name})
            VALUES (%s, %s)
        """
        pg_cursor.executemany(insert_query, new_docs)
        pg_conn.commit()
        print(f"✅ Inserted {len(new_docs)} new rows into '{pg_table}'")
    else:
        print(f"⚠️ No new documents to insert into '{pg_table}'")

    pg_cursor.close()


# === Connect to MongoDB === This might need updated to have username/pass
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_db_name = os.getenv("MONGO_DB_NAME", "lstats_p_mongo")
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[mongo_db_name]
timeline_collection = mongo_db[os.getenv("MONGO_TIMELINE_COLLECTION", "timeline_json")]
data_collection = mongo_db[os.getenv("MONGO_DATA_COLLECTION", "data_json")]

# === Connect to PostgreSQL ===
pg_conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT"))
)

# === Run the copies ===
copy_mongo_to_postgres(
    mongo_collection=timeline_collection,
    json_field_name="json_timeline",
    pg_table="json_timeline",
    pg_conn=pg_conn
)

copy_mongo_to_postgres(
    mongo_collection=data_collection,
    json_field_name="json_data",
    pg_table="json_data",
    pg_conn=pg_conn
)

# === Cleanup ===
pg_conn.close()
mongo_client.close()
