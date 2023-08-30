from typing import Dict
from typing import List
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from utils import backoff
from storage.elasticsearch_index_schema import INDEX_SCHEMA


class ElasticSaver:
    schema = INDEX_SCHEMA

    def __init__(self, connection: Elasticsearch, index: str) -> None:
        self.conn = connection
        self.index = index

    @backoff()
    def bulk_insert(self, data: List[Dict]) -> tuple:
        return bulk(self.conn, data, index='movies')

    def index_exists(self) -> bool:
        return self.conn.indices.exists(index=self.index)

    def index_create(self):
        return self.conn.indices.create(index=self.index, body=self.schema)
