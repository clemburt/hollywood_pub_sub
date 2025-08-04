"""Module defining the Movie model used to represent film entries."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Movie(BaseSettings):
    """Movie model representing a single film entry."""

    title: str
    director: str
    composer: str
    cast: list[str]
    year: int

    model_config = ConfigDict(extra="forbid")  # Disallow unexpected fields
