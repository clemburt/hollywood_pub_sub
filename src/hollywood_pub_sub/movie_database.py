"""Module defining the abstract MovieDatabase base class for handling movie collections."""

from abc import ABC, abstractmethod
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, validate_call

from hollywood_pub_sub.movie import Movie


class MovieDatabase(BaseModel, ABC):
    """
    Abstract base class representing a collection of Movie instances.

    Provides filtering and JSON export methods based on a `movies` property
    that must be implemented by subclasses.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def movies(self) -> list[Movie]:
        """Return list of Movie instances (must be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement the 'movies' property.")

    @validate_call
    def filter(
        self,
        title: str | None = None,
        director: str | None = None,
        composer: str | None = None,
        year: int | None = None,
        cast: str | list[str] | None = None,
    ) -> list[Movie]:
        """
        Filter movies based on various attributes.

        Parameters
        ----------
        title : Optional[str]
            Exact title to match.
        director : Optional[str]
            Exact director name to match.
        composer : Optional[str]
            Exact composer name to match.
        year : Optional[int]
            Release year to match.
        cast : Optional[Union[str, List[str]]]
            One or more cast members that must appear in the movie.

        Returns
        -------
        List[Movie]
            Filtered list of movies matching all specified criteria.

        """
        cast_filter: list[str] | None = [cast] if isinstance(cast, str) else cast

        def match(movie: Movie) -> bool:
            if title and movie.title != title:
                return False
            if director and movie.director != director:
                return False
            if composer and movie.composer != composer:
                return False
            if year and movie.year != year:
                return False
            if cast_filter and not all(actor in movie.cast for actor in cast_filter):
                return False
            return True

        return [movie for movie in self.movies if match(movie)]

    @validate_call
    def to_json(self, path: Path | None = None, indent: int = 4) -> str | None:
        """
        Export movies to JSON format.

        Parameters
        ----------
        path : Optional[Path]
            Path to save the JSON file. If not provided, returns the JSON string.
        indent : int
            Indentation level for JSON formatting.

        Returns
        -------
        Optional[str]
            JSON string if no path is provided, otherwise None.

        """
        data = [movie.model_dump() for movie in self.movies]
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)

        if path is not None:
            path.write_text(json_str, encoding="utf-8")
            return None
        return json_str
