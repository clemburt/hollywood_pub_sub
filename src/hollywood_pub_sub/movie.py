from typing import List, Optional

from pydantic import BaseModel


class Movie(BaseModel):
    """
    Movie data model.

    Attributes
    ----------
    title : str
        Title of the movie.
    director : str
        Director of the movie.
    composer : str
        Composer who created the original score.
    cast : List[str]
        Main actors in the movie (up to 3).
    year : Optional[int]
        Year the movie was released.
    """
    title: str
    director: str
    composer: str
    cast: List[str]
    year: Optional[int]

