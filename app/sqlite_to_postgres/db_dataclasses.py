import uuid
from dataclasses import dataclass, field, fields
from datetime import datetime


@dataclass
class Filmwork:
    title: str
    description: str
    creation_date: datetime
    type: str
    created_at: datetime
    updated_at: datetime
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    full_name: str
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmwork:
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork:
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    role: str
    created_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


TABLES = {
    'film_work': Filmwork,
    'person': Person,
    'genre': Genre,
    'genre_film_work': GenreFilmwork,
    'person_film_work': PersonFilmwork,
}


FIELD_MATCHING = {
    'created_at': 'created',
    'updated_at': 'modified',
}


def get_fields(data_type: type) -> list:
    return [fld.name for fld in fields(data_type)]


def get_fields_types(data_type: type) -> str:
    types = []
    for fld in fields(data_type):
        if fld.type is str:
            types.append('text')
        if fld.type is uuid.UUID:
            types.append('uuid')
        if fld.type is datetime:
            if fld.name == 'creation_date':
                types.append('date')
            else:
                types.append('timestamp with time zone')
        if fld.type is float:
            types.append('double precision')

    return types