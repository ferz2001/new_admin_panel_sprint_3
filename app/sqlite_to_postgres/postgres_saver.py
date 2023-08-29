from db_dataclasses import TABLES, FIELD_MATCHING, get_fields, get_fields_types

from psycopg2.extensions import connection


class PostgresSaver:

    def __init__(self, conn: connection) -> None:
        self.conn = conn

    def save_data(self, table_name: str, data: list) -> None:
        cur = self.conn.cursor()

        TableDataClass = TABLES[table_name]
        table_fields = get_fields(TableDataClass)
        table_field_types = get_fields_types(TableDataClass)

        _table_fields = []
        for fld in table_fields:
            _table_fields.append(FIELD_MATCHING.get(fld, fld))

        values = [f'${i}' for i in range(1, len(_table_fields) + 1)]

        sql_query = 'PREPARE temp_table_insert(' + ', '.join(table_field_types) + ')' + \
            f' AS INSERT INTO content.{table_name} (' + ', '.join(_table_fields) + \
            ') VALUES (' + ', '.join(values) + ') ON CONFLICT (id) DO NOTHING;'
        cur.execute(sql_query)
        self.conn.commit()

        sql_query = 'BEGIN;'
        for i in range(len(data)):
            values = []
            for field in table_fields:
                value = str(getattr(data[i], field)).replace('\'', '\'\'')
                value = 'NULL' if value == 'None' else '\'' + value + '\''
                values.append(value)

            sql_query += ('EXECUTE temp_table_insert(' + ', '.join(values) + ');')

        sql_query += 'COMMIT;'

        self.conn.autocommit = False
        cur.execute(sql_query)
        self.conn.commit()
        self.conn.autocommit = True

        sql_query = 'DEALLOCATE temp_table_insert;'
        cur.execute(sql_query)
        cur.close()
