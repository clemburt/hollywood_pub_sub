"""Generate the movie_database.json file by querying the TMDB API."""

import os
from pathlib import Path

from hollywood_pub_sub.movie_database_from_api import MovieDatabaseFromAPI


def main() -> None:
    """
    Generate the movie_database.json file by querying the TMDB API.

    Returns
    -------
    None

    """
    # Build movie database with movies from TMDb API
    api_key = os.getenv("TMDB_API_KEY")
    movie_db = MovieDatabaseFromAPI(
        api_key=api_key,
        composers=[
            "Bernard Herrmann",
            "Jerry Goldsmith",
            "John Barry",
            "John Williams",
            "Michel Legrand",
        ],
        max_movies_per_composer=5,
    )
    movie_db.to_json(path=Path("movie_database.json"))


if __name__ == "__main__":
    main()
