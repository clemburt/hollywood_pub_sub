from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Movie(BaseSettings):
    """
    Movie model representing a single film entry.

    Attributes
    ----------
    title : str
        The title of the movie.
    director : str
        The director of the movie.
    composer : str
        The composer of the soundtrack.
    cast : List[str]
        List of main cast members.
    year : int
        The release year of the movie.
    """

    title: str
    director: str
    composer: str
    cast: List[str]
    year: int

    model_config = ConfigDict(
        extra="forbid"  # Disallow unexpected fields
    )
