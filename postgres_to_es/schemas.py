from uuid import UUID
from typing import List
from typing import Union

from pydantic import BaseModel


class PersonSchema(BaseModel):
    id: UUID
    name: str


class MoviesSchema(BaseModel):
    id: UUID
    imdb_rating: Union[float, None] = None
    genre: List
    title: str
    description: str
    director: List
    actors_names: List[str]
    writers_names: List
    actors: List[PersonSchema]
    writers: List[PersonSchema]
