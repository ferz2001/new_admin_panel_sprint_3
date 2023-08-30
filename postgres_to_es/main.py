import sys
from datetime import datetime
from time import sleep

import elasticsearch

from logger import logger
from settings import Settings
from storage.elasticsearch import ElasticSaver
from storage.postgres import PostgresConn, PostgresExtractor
from state import State, JsonFileStorage


def main(state: State, postgres_extractor: PostgresExtractor, elastic_saver: ElasticSaver) -> None:
    logger.info('start upload data')

    last_upload_id = state.get_state('upload_last_id')
    if not last_upload_id:
        logger.info('first run upload')
        state.set_state('upload_started_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    upload_started_at = state.get_state('upload_started_at')
    logger.info(f'upload_started_at = {upload_started_at}')

    data = postgres_extractor.extract_table_data(before_date=upload_started_at, last_upload_id=last_upload_id)
    for chunk_data in data:
        result = elastic_saver.bulk_insert(chunk_data)
        logger.debug(result)
        logger.debug('===================================')

        state.set_state('upload_last_id', chunk_data[-1]['id'])

    state.set_state('upload_complete_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))


def find_updated(state: State, postgres_extractor: PostgresExtractor, elastic_saver: ElasticSaver) -> None:
    logger.info('start updating data')

    update_started_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    updated_after = state.get_state('update_started_at')
    if not updated_after:
        updated_after = state.get_state('upload_started_at')

    logger.debug(updated_after)

    for method_name in ['get_updated_person', 'get_updated_genre', 'get_updated_filmwork']:
        data = getattr(postgres_extractor, method_name)(updated_after=updated_after)
        logger.debug(method_name)
        for chunk_data in data:
            logger.debug(chunk_data)
            result = elastic_saver.bulk_insert(chunk_data)
            logger.debug(result)
        logger.debug('-------------------------------------')

    state.set_state(key='update_started_at', value=update_started_at)


if __name__ == '__main__':
    try:
        settings = Settings()

        storage = JsonFileStorage(file_path='data.json')
        app_state = State(storage=storage)

        es_client = elasticsearch.Elasticsearch(hosts=settings.ES_URL)
        es_saver = ElasticSaver(connection=es_client, index='movies')

        index_exists = es_saver.index_exists()
        if not index_exists:
            logger.info('Index not exists, creating')
            es_saver.index_create()

        dsn = {
            'dbname': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'options': settings.DB_OPTIONS,
        }

        with PostgresConn(db_config=dsn) as pg_conn:
            pg_extractor = PostgresExtractor(connection=pg_conn)

            upload_complete = app_state.get_state('upload_complete_at')

            if not upload_complete:
                logger.info('upload not comlete')
                main(state=app_state, postgres_extractor=pg_extractor, elastic_saver=es_saver)

            logger.info('upload comlete')

            while True:
                find_updated(state=app_state, postgres_extractor=pg_extractor, elastic_saver=es_saver)
                logger.info('sleep')
                sleep(settings.POLING_DATA_INTERVAL)

    except KeyboardInterrupt:
        sys.exit()
