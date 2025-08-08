import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# All scripts should include django settings.
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolData.settings")
django.setup()

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# MySQL and PostgreSQL connection URIs
MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
POSTGRES_URI = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engines
mysql_engine = create_engine(MYSQL_URI)
postgres_engine = create_engine(POSTGRES_URI)

# Reflect metadata without using 'bind'
mysql_metadata = MetaData()
mysql_metadata.reflect(bind=mysql_engine)

postgres_metadata = MetaData()

# Create tables in PostgreSQL if they don't exist
mysql_metadata.create_all(postgres_engine)

# Create sessions
MySQLSession = sessionmaker(bind=mysql_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

mysql_session = MySQLSession()
postgres_session = PostgresSession()

try:
    for table_name, table in mysql_metadata.tables.items():
        print(f"Transferring table: {table_name}")
        # Reflect the same table in PostgreSQL
        pg_table = Table(table_name, postgres_metadata, autoload_with=postgres_engine)

        # Read from MySQL
        rows = mysql_session.execute(table.select()).fetchall()

        if rows:
            # Insert into PostgreSQL
            postgres_session.execute(pg_table.insert(), [row._mapping for row in rows])
            postgres_session.commit()
            print(f"✅ {len(rows)} rows copied into {table_name}")
        else:
            print(f"⚠️ No rows in {table_name}, skipping.")

except SQLAlchemyError as e:
    print("❌ Error occurred:", e)
    postgres_session.rollback()

finally:
    mysql_session.close()
    postgres_session.close()
