import pytest
from unittest.mock import patch

from hollywood_pub_sub.main import run_game
from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.movie_database import MovieDatabase


def test_run_game_with_mocked_api():
    """
    Test run_game with mocked TMDb API calls and injected movies.
    Verifies a winner is declared when threshold is reached.
    """

    # Prepare test movies
    test_movies = [
        Movie(
            title="Test Movie 1",
            director="Director 1",
            composer="Composer A",
            cast=["Actor 1", "Actor 2"],
            year=2000
        ),
        Movie(
            title="Test Movie 2",
            director="Director 2",
            composer="Composer B",
            cast=["Actor 3", "Actor 4"],
            year=2001
        ),
        Movie(
            title="Test Movie 3",
            director="Director 3",
            composer="Composer A",
            cast=["Actor 5"],
            year=2002
        ),
        Movie(
            title="Test Movie 4",
            director="Director 4",
            composer="Composer A",
            cast=["Actor 6"],
            year=2003
        ),
        Movie(
            title="Test Movie 5",
            director="Director 5",
            composer="Composer A",
            cast=["Actor 7"],
            year=2004
        ),
    ]

    # Patch the _fetch_movies_from_api method to do nothing (skip real API calls)
    with patch.object(MovieDatabase, "_fetch_movies_from_api", return_value=None):
        # Create an instance normally (no real API call due to patch)
        movie_db = MovieDatabase(api_key="fake_api_key", max_movies_per_composer=10)
        # Inject the test movies list
        movie_db.movies = test_movies
        # Inject composers list explicitly
        movie_db.COMPOSERS = ["Composer A", "Composer B"]

        # Patch MovieDatabase inside main to return our patched instance
        with patch("hollywood_pub_sub.main.MovieDatabase", return_value=movie_db):
            # Patch logger.info to capture logs
            with patch("hollywood_pub_sub.logger.logger.info") as mock_logger_info:
                run_game(
                    api_key="fake_api_key",
                    max_movies_per_composer=10,
                    winning_threshold=3,
                )

                # Check that winner message was logged at least once
                winner_logs = [
                    call.args[0]
                    for call in mock_logger_info.call_args_list
                    if "Winner is subscriber composer" in call.args[0]
                ]
                assert winner_logs, "Winner message was not logged"


if __name__ == "__main__":
    pytest.main()
