import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, validate_call

from hollywood_pub_sub.movie import Movie
# from hollywood_pub_sub.settings import ComposerSettings  # Plus nécessaire


class MovieDatabase(BaseModel, ABC):
    """
    Abstract base class representing a collection of Movie instances.

    Provides filtering and JSON export methods based on a `movies` property
    that must be implemented by subclasses.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Suppression de l'attribut composers
    # composers: List[str] = Field(default_factory=lambda: ComposerSettings().composers)

    @property
    @abstractmethod
    def movies(self) -> List[Movie]:
        """
        List of Movie instances. Must be implemented by subclasses.

        Returns
        -------
        List[Movie]
        """
        raise NotImplementedError("Subclasses must implement the 'movies' property.")

    @validate_call
    def filter(
        self,
        title: Optional[str] = None,
        director: Optional[str] = None,
        composer: Optional[str] = None,
        year: Optional[int] = None,
        cast: Optional[Union[str, List[str]]] = None,
    ) -> List[Movie]:
        """
        Filter movies based on various attributes.

        Parameters
        ----------
        title : Optional[str], optional
            Exact title to match.
        director : Optional[str], optional
            Exact director name to match.
        composer : Optional[str], optional
            Exact composer name to match.
        year : Optional[int], optional
            Release year to match.
        cast : Optional[Union[str, List[str]]], optional
            One or more cast members that must appear in the movie.

        Returns
        -------
        List[Movie]
            Filtered list of movies matching all specified criteria.
        """
        cast_filter: Optional[List[str]] = [cast] if isinstance(cast, str) else cast

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
    def to_json(self, path: Optional[Path] = None, indent: int = 4) -> Optional[str]:
        """
        Export movies to JSON format.

        Parameters
        ----------
        path : Optional[Path], optional
            Path to save the JSON file. If not provided, returns the JSON string.
        indent : int, optional
            Indentation level for JSON formatting. Default is 4.

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
