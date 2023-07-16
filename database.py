import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = ""
DB_PASSWORD = ""
DB_NAME = "mail-sender-db"

Base = declarative_base()

# Create an engine
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def create_database(database_name):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
    )

    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {database_name}")
    cursor.close()
    conn.close()

def create_database_if_not_exists(database_name: str):
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        dbname="postgres",
    )

    conn.autocommit = True  # Disable autocommit

    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database_name}'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully")

    cursor.close()
    conn.close()


create_database_if_not_exists(DB_NAME)
