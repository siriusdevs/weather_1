import os

import psycopg
from dotenv import load_dotenv

import query


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


def get_all_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute(query.SELECT_CITY)
    return cursor.fetchall()


def get_cities(cursor: psycopg.Cursor, attrs: list, attr_values: list) -> list[tuple]:
    query_params = make_up_values(attrs, sep=' and ')
    select_query = query.SELECT_CITIES_PARAMETRISED.format(params=query_params)
    cursor.execute(select_query, params=attr_values)
    return cursor.fetchall()


def add_city(cursor: psycopg.Cursor, connection: psycopg.Connection, city: tuple) -> bool:
    cursor.execute(query.INSERT_CITY, params=city)
    connection.commit()
    return bool(cursor.rowcount)


def delete_city(cursor: psycopg.Cursor, connection: psycopg.Connection, city_name: str) -> bool:
    cursor.execute(query.DELETE_BY_NAME, params=(city_name,))
    connection.commit()
    return bool(cursor.rowcount)


def coordinates_by_city(cursor: psycopg.Cursor, city_name: str) -> tuple[float]:
    cursor.execute(query.COORD_BY_CITY, params=(city_name,))
    return cursor.fetchone()


def check_token(cursor: psycopg.Cursor, token: str) -> bool:
    cursor.execute(query.CHECK_TOKEN, params=(token,))
    return bool(cursor.fetchall())


def make_up_values(new_attrs: list, sep: str = ', ') -> str:
    return sep.join(f'{attr}=%s' for attr in new_attrs)


def update_city(
    cursor: psycopg.Cursor,
    connection: psycopg.Connection,
    city_name: str,
    new_city_params: dict,
) -> bool:
    attrs, attr_values = [], []
    for attr, new_value in new_city_params.items():
        attrs.append(attr)
        attr_values.append(new_value)
    attr_values.append(city_name)
    attrs = make_up_values(attrs)
    cursor.execute(query.UPDATE_CITY.format(params=attrs), params=attr_values)
    connection.commit()
    return bool(cursor.rowcount)
