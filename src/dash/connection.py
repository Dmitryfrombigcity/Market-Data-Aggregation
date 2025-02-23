import psycopg

from src.db.config import setting


def get_connection():
    with psycopg.connect(conninfo=setting.uri) as conn:
        while True:
            yield conn


connection = get_connection()
conn = next(connection)
