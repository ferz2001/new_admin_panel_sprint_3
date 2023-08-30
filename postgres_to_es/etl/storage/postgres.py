from typing import Dict, List, Union
from types import TracebackType
from collections.abc import Iterator

import psycopg2
from psycopg2.extras import DictCursor
from utils import backoff


class PostgresConn:
    def __init__(self, db_config: Dict):
        self.db_conn = None
        self.db_config = db_config

    @backoff()
    def __enter__(self) -> psycopg2.extensions.connection:
        self.db_conn = psycopg2.connect(**self.db_config, cursor_factory=DictCursor)
        return self.db_conn


    def __exit__(self, exception_type: Union[type[BaseException], None], exception_value: Union[BaseException, None], traceback: Union[TracebackType, None]) -> None:
        if self.db_conn:
            self.db_conn.close()


class PostgresExtractor:
    SQL = '''
        SELECT
            "content"."film_work"."id",
            "content"."film_work"."id" AS "_id",
            "content"."film_work"."rating" AS "imdb_rating",
            "content"."film_work"."title",
            COALESCE(
                "content"."film_work"."description",
                ''
            ) AS "description",

            COALESCE (
                ARRAY_AGG( DISTINCT "content"."genre"."name" ),
                '{}'
            ) AS "genre",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") FILTER (WHERE "content"."person_film_work"."role" = 'director'),
                '{}'
            ) AS "director",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") FILTER (WHERE "content"."person_film_work"."role" = 'actor'),
                '{}'
            ) AS "actors_names",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") FILTER (WHERE "content"."person_film_work"."role" = 'writer'),
                '{}'
            ) AS "writers_names",

            COALESCE (
                JSONB_AGG(
                    DISTINCT jsonb_build_object(
                        'id', "content"."person"."id",
                        'name', "content"."person"."full_name"
                    )
                ) FILTER (WHERE "content"."person_film_work"."role" = 'actor'),
                '[]'
            ) AS "actors",

            COALESCE (
                JSONB_AGG(
                    DISTINCT jsonb_build_object(
                        'id', "content"."person"."id",
                        'name', "content"."person"."full_name"
                    )
                ) FILTER (WHERE "content"."person_film_work"."role" = 'writer'),
                '[]'
            ) AS "writers"

        FROM "content"."film_work"
        LEFT OUTER JOIN "content"."genre_film_work" ON ("content"."film_work"."id" = "content"."genre_film_work"."film_work_id")
        LEFT OUTER JOIN "content"."genre" ON ("content"."genre_film_work"."genre_id" = "content"."genre"."id")
        LEFT OUTER JOIN "content"."person_film_work" ON ("content"."film_work"."id" = "content"."person_film_work"."film_work_id")
        LEFT OUTER JOIN "content"."person" ON ("content"."person_film_work"."person_id" = "content"."person"."id")
    '''

    def __init__(self, connection: psycopg2.extensions.connection, chunk_size: int = 100) -> None:
        self.conn = connection
        self.chunk_size = chunk_size


    @backoff()
    def _fetch_chunked(self, sql: str, params: Union[tuple, None] = None) -> Iterator:
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                while chunk := cur.fetchmany(self.chunk_size):
                    yield chunk


    def extract_table_data(self, before_date: str, upload_last_id: Union[str, None] = None) -> List:
        sql = self.SQL + 'WHERE "content"."film_work"."modified" <= %s'
        params = (before_date,)

        if upload_last_id:
            sql += 'AND "content"."film_work"."id" > %s'
            params += (upload_last_id,)

        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=params)


    def get_updated_filmwork(self, updated_after: str) -> List:
        sql = self.SQL + '''
        WHERE "content"."film_work"."id" IN (
            SELECT film_work.id
            FROM film_work
            WHERE modified > %s
        )
        '''
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))


    def get_updated_person(self, updated_after: str) -> List:
        sql = self.SQL + '''
        WHERE "content"."film_work"."id" IN (
            SELECT film_work.id
            FROM person
            LEFT JOIN person_film_work ON person_film_work.person_id = person.id
            LEFT JOIN film_work ON film_work.id = person_film_work.film_work_id
            WHERE person.modified > %s
        )
        '''
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))


    def get_updated_genre(self, updated_after: str) -> List:
        sql = self.SQL + '''
        WHERE "content"."film_work"."id" IN (
            SELECT film_work.id
            FROM genre
            LEFT JOIN genre_film_work ON genre_film_work.genre_id = genre.id
            LEFT JOIN film_work ON film_work.id = genre_film_work.film_work_id
            WHERE genre.modified > %s
        )
        '''
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))
