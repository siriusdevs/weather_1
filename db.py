import os

import psycopg
from dotenv import load_dotenv

from config import CITIES_SELECT, CITIES_INSERT, CITIES_DELETE_BY_NAME, CITIES_COORD_BY_CITY


def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
    load_dotenv()
    try:
        port = int(os.environ.get('PG_PORT', default='5432'))
    except ValueError:
        port = 5555

    credentials = {
        'host': os.environ.get('PG_HOST', default='127.0.0.1'),
        'port': port,
        'dbname': os.environ.get('PG_DBNAME', default='test'),
        'user': os.environ.get('PG_USER', default='test'),
        'password': os.environ.get('PG_PASSWORD'),
    }
    connection = psycopg.connect(**credentials)
    return connection, connection.cursor()


def get_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute(CITIES_SELECT)
    return cursor.fetchall()


def add_city(cursor: psycopg.Cursor, connection: psycopg.Connection, city: tuple) -> bool:
    cursor.execute(CITIES_INSERT, params=city)
    connection.commit()
    return bool(cursor.rowcount)


def delete_city(cursor: psycopg.Cursor, connection: psycopg.Connection, city_name: str) -> bool:
    cursor.execute(CITIES_DELETE_BY_NAME, params=(city_name,))
    connection.commit()
    return bool(cursor.rowcount)


def coordinates_by_city(cursor: psycopg.Cursor, city_name: str) -> tuple[float]:
    cursor.execute(CITIES_COORD_BY_CITY, params=(city_name,))
    return cursor.fetchone()
