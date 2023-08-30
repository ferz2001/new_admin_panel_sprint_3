from typing import Tuple
import db_dataclasses

from sqlite3 import Connection


class SQLiteLoader:

    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def load_movies_database(
        self,
        pack_size: int = 500
    ) -> Tuple[str, list]:

        for table_name in db_dataclasses.TABLES.keys():
            yield from self.load_table(table_name, pack_size)

    def load_table(self, table_name: str, pack_size: int) -> Tuple[str, list]:
        TableDataClass = db_dataclasses.TABLES[table_name]
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM {table_name};')

        data = []
        while True:
            data.clear()
            result = cur.fetchmany(pack_size)
            if not result:
                return table_name, data

            for row in result:
                kwarg = {}
                for fld in db_dataclasses.get_fields(TableDataClass):
                    kwarg[fld] = row[fld]
                data.append(TableDataClass(**kwarg))

            yield table_name, data
        cur.close()
