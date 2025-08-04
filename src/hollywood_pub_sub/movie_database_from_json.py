"""Module providing MovieDatabaseFromJSON, a root model for movies loaded from JSON."""

from typing import Self

from pydantic import FilePath, RootModel, validate_call

from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.movie_database import MovieDatabase


class MovieDatabaseFromJSON(RootModel[list[Movie]], MovieDatabase):
    """
    A root model representing a database of movies.

    Uses a list of Movie instances as its root.
    """

    @property
    def movies(self) -> list[Movie]:
        """Return the list of movies stored in the root."""
        return self.root

    @property
    def composers(self) -> list[str]:
        """Return a sorted list of unique composers from the movies."""
        composers_set: set[str] = {movie.composer for movie in self.root if movie.composer}
        return sorted(composers_set)

    @classmethod
    @validate_call
    def from_json(cls, path: FilePath) -> Self:
        """
        Load and validate the movie database from a JSON file.

        Parameters
        ----------
        path : FilePath
            Path to the JSON file.

        Returns
        -------
        Self
            An instance of MovieDatabaseFromJSON with validated movies.

        """
        return cls.model_validate_json(path.read_bytes())
