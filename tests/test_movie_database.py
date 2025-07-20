from pathlib import Path
from typing import Optional
from unittest.mock import patch, MagicMock

import pytest

from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.movie_database import MovieDatabase
import hollywood_pub_sub.movie_database as movie_db_module


@pytest.fixture
def movie_db_json_path() -> Path:
    """
    Provides the path to the fixed movie database JSON fixture.
    Assumes the file exists at tests/fixtures/movie_database.json
    """
    path = Path("tests/fixtures/movie_database.json")
    if not path.is_file():
        pytest.skip(f"Fixture file not found: {path}")
    return path


def test_load_movies_from_fixed_json(movie_db_json_path: Path) -> None:
    """
    Test that MovieDatabase correctly loads and parses movies from
    the provided fixed JSON file (tests/fixtures/movie_database.json).
    """
    db = MovieDatabase(json_path=movie_db_json_path)
    # Basic sanity checks on the loaded movies
    assert len(db.movies) > 0
    first_movie = db.movies[0]
    assert isinstance(first_movie, Movie)
    assert isinstance(first_movie.title, str)
    assert isinstance(first_movie.director, str)
    assert isinstance(first_movie.composer, str)
    assert isinstance(first_movie.cast, list)
    assert isinstance(first_movie.year, int)


@pytest.fixture
def fake_api_key() -> str:
    """
    Returns a dummy API key string for TMDb API tests.
    """
    return "fake-api-key"


@patch.object(movie_db_module.MovieDatabase, "tmdb_get")
def test_search_person_returns_valid_composer_id(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    """
    Test search_person returns the correct TMDb ID for a composer,
    filtering by music-related department.
    """
    mock_tmdb_get.return_value = {
        "results": [
            {"id": 555, "name": "Hans Zimmer", "known_for_department": "Music", "popularity": 15.0},
            {"id": 666, "name": "Some Actor", "known_for_department": "Acting", "popularity": 20.0}
        ]
    }
    db = MovieDatabase(api_key=fake_api_key)
    composer_id: Optional[int] = db.search_person("Hans Zimmer")
    assert composer_id == 555


@patch.object(movie_db_module.MovieDatabase, "tmdb_get")
def test_get_person_credits_returns_crew_dict(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    """
    Test that get_person_credits returns a dict containing 'crew' key.
    """
    mock_tmdb_get.return_value = {
        "crew": [{"job": "Composer", "id": 1, "title": "Test Movie"}]
    }
    db = MovieDatabase(api_key=fake_api_key)
    credits = db.get_person_credits(123)
    assert isinstance(credits, dict)
    assert "crew" in credits


@patch.object(movie_db_module.MovieDatabase, "tmdb_get")
def test_get_movie_details_extracts_director_and_cast(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    """
    Test get_movie_details returns expected movie data including credits,
    and that the director extraction and main cast extraction methods work correctly.
    """
    mock_tmdb_get.return_value = {
        "title": "Inception",
        "release_date": "2010-07-16",
        "credits": {
            "cast": [
                {"name": "Leonardo DiCaprio"},
                {"name": "Joseph Gordon-Levitt"},
                {"name": "Ellen Page"}
            ],
            "crew": [
                {"job": "Director", "name": "Christopher Nolan"},
                {"job": "Producer", "name": "Emma Thomas"}
            ]
        }
    }
    db = MovieDatabase(api_key=fake_api_key)
    details = db.get_movie_details(1)
    director = db._extract_director(details)
    main_cast = db.extract_main_cast(details["credits"])

    assert details["title"] == "Inception"
    assert director == "Christopher Nolan"
    assert main_cast == ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"]


@patch.object(movie_db_module.MovieDatabase, "search_person")
@patch.object(movie_db_module.MovieDatabase, "get_person_credits")
@patch.object(movie_db_module.MovieDatabase, "get_movie_details")
def test_fetch_movies_from_api_populates_movies(
    mock_get_movie_details: MagicMock,
    mock_get_person_credits: MagicMock,
    mock_search_person: MagicMock,
    fake_api_key: str,
) -> None:
    """
    Test _fetch_movies_from_api populates movies list with mocked TMDb API calls.
    """
    mock_search_person.return_value = 777

    mock_get_person_credits.return_value = {
        "crew": [
            {"id": 10, "job": "Original Music Composer", "title": "Fake Movie 1"},
            {"id": 20, "job": "Composer", "title": "Fake Movie 2"}
        ]
    }

    mock_get_movie_details.side_effect = [
        {
            "title": "Fake Movie 1",
            "release_date": "2005-01-01",
            "credits": {
                "cast": [{"name": "Actor 1"}, {"name": "Actor 2"}],
                "crew": [{"job": "Director", "name": "Director 1"}]
            }
        },
        {
            "title": "Fake Movie 2",
            "release_date": "2007-02-02",
            "credits": {
                "cast": [{"name": "Actor 3"}, {"name": "Actor 4"}],
                "crew": [{"job": "Director", "name": "Director 2"}]
            }
        }
    ]

    db = movie_db_module.MovieDatabase(
        api_key=fake_api_key,
        max_movies_per_composer=2,
        COMPOSERS=["Fake Composer"]
    )

    assert len(db.movies) == 2
    assert db.movies[0].composer == "Fake Composer"
    assert db.movies[0].title == "Fake Movie 1"
    assert db.movies[1].composer == "Fake Composer"
    assert db.movies[1].title == "Fake Movie 2"


def test_error_raised_if_no_api_key_or_json_path() -> None:
    """
    Test that initializing MovieDatabase without json_path or api_key
    raises a ValueError.
    """
    with pytest.raises(ValueError):
        MovieDatabase()
