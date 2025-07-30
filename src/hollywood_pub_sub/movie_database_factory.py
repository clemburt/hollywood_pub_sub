from pathlib import Path
from typing import Optional, Union

from hollywood_pub_sub.movie_database import MovieDatabase
from hollywood_pub_sub.movie_database_from_json import MovieDatabaseFromJSON
from hollywood_pub_sub.movie_database_from_api import MovieDatabaseFromAPI


def movie_database_factory(
    max_movies_per_composer: int,
    api_key: Optional[str] = None,
    json_path: Optional[Union[str, Path]] = None,
) -> MovieDatabase:
    """
    Factory function to build a MovieDatabase from either a JSON file or the TMDb API.

    Parameters
    ----------
    max_movies_per_composer : int
        Number of movies to fetch per composer (used with API).
    json_path : str or Path, optional
        Path to the local JSON file. If provided, it takes precedence over API fetching.
    api_key : str, optional
        TMDb API key. Required if `json_path` is not provided.

    Returns
    -------
    MovieDatabase
        A MovieDatabase instance built from JSON or API.

    Raises
    ------
    ValueError
        If neither `json_path` nor `api_key` is provided.
    """
    if json_path is not None:
        return MovieDatabaseFromJSON.from_json(Path(json_path))
    elif api_key is not None:
        return MovieDatabaseFromAPI(
            api_key=api_key,
            max_movies_per_composer=max_movies_per_composer,
        )
    else:
        raise ValueError("You must provide either a JSON path or a TMDb API key.")
