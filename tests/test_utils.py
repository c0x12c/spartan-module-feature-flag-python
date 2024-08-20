import os
import string

import psycopg2
import redis

from faker import Faker

fake = Faker()


def get_db_connection():
    connection = psycopg2.connect(
        dbname="local", user="local", password="local", host="localhost", port="5432"
    )
    return connection


def get_redis_connection():
    return redis.Redis(host="localhost", port=6379, db=0)


def setup_database(connection, sql_file="setup.sql"):
    # Get the absolute path to the SQL file
    sql_file_path = os.path.join(os.path.dirname(__file__), sql_file)

    with connection.cursor() as cursor:
        with open(sql_file_path, "r") as f:
            cursor.execute(f.read())
        connection.commit()


def teardown_database(connection):
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS feature_flags;")
        connection.commit()


def random_word(length=10):
    return "".join(fake.random_choices(elements=string.ascii_lowercase, length=length))
