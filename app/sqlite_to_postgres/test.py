import os
import psycopg2

from sqlite3 import connect as sqlite_connect, Row, Connection
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from datetime import datetime
from dotenv import load_dotenv
from contextlib import contextmanager
from db_dataclasses import TABLES, FIELD_MATCHING, get_fields


@contextmanager
def sqlite_context(db_path: str):
    conn = sqlite_connect(db_path)
    conn.row_factory = Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def pg_context(**dsl):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        yield conn
    finally:
        conn.close()


def table_row_count(conn: _connection | Connection, table_name: str) -> int:
    cur = conn.cursor()
    sql_query = f'SELECT COUNT(*) as count FROM {table_name};'
    cur.execute(sql_query)
    cur.close()
    result = cur.fetchone()
    if result is None:
        return 0

    return result[0]


def test_integrity(db_conf):
    with sqlite_context('db.sqlite') as sqlite_conn,\
            pg_context(**db_conf) as pg_conn:

        for table_name in TABLES.keys():
            pg_count = table_row_count(pg_conn, f'content.{table_name}')
            sqlite_count = table_row_count(sqlite_conn, table_name)
            assert pg_count == sqlite_count, "Число записей в БД отличается"


def check_records(
    sqlite_conn: Connection,
    pg_conn: _connection,
    table_name: str
) -> int:

    sqlite_query = f'SELECT * FROM {table_name} ORDER BY id;'
    sqlite_cur = sqlite_conn.cursor()

    pg_query = f'SELECT * FROM content.{table_name} ORDER BY id;'
    pg_cur = pg_conn.cursor()

    t_fields = get_fields(TABLES[table_name])
    pg_cur.execute(pg_query)

    format_str = "%Y-%m-%d %H:%M:%S.%f%z"

    matching_values = zip(sqlite_cur.execute(sqlite_query), pg_cur.fetchall())
    pg_cur.close()
    sqlite_cur.close()
    for sqlite_row, pg_row in matching_values:
        for field in t_fields:
            pg_fld = FIELD_MATCHING.get(field, field)
            sqlite_value = sqlite_row[field]
            pg_value = pg_row[pg_fld]
            if isinstance(pg_value, datetime):
                sqlite_dt = datetime.strptime(sqlite_value + '00', format_str)
                sqlite_value = datetime.timestamp(sqlite_dt)
                pg_value = datetime.timestamp(pg_value)

            if sqlite_value != pg_value:
                return False

    return True


def test_consistency(db_conf):
    with sqlite_context('db.sqlite') as sqlite_conn,\
            pg_context(**db_conf) as pg_conn:

        for table_name in TABLES:
            assert check_records(sqlite_conn, pg_conn, table_name), "Есть неправильно записанные данные"


if __name__ == '__main__':
    load_dotenv()

    db_conf = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5432),
    }

    test_integrity(db_conf)
    test_consistency(db_conf)

