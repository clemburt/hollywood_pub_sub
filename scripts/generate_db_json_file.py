import os

from hollywood_pub_sub.movie_database_factory import MovieDatabaseFactory


def main() -> None:
    """
    Generate file movie_database.json by querying the TMDB api

    Returns
    -------
    None
    """
    # Step 1: Build movie database with movies from TMDb API
    api_key = os.getenv("TMDB_API_KEY")
    movie_db = MovieDatabaseFactory(
        api_key=api_key,
        COMPOSERS=[
            "Bernard Herrmann",
            "Jerry Goldsmith",
            "John Barry",
            "John Williams",
            "Michel Legrand",
        ],
        max_movies_per_composer=5,
    )
    movie_db.export_to_json(path="movie_database.json")


if __name__ == "__main__":
    main()
