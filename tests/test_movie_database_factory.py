from pathlib import Path
from unittest.mock import patch

import pytest

from hollywood_pub_sub.movie_database_factory import movie_database_factory
from hollywood_pub_sub.movie_database_from_json import MovieDatabaseFromJSON


@pytest.fixture
def movie_database_json_path() -> Path:
    path = Path("tests/fixtures/movie_database.json")
    if not path.is_file():
        pytest.skip(f"Fixture file not found: {path}")
    return path


def test_factory_loads_from_json(movie_database_json_path):
    db = movie_database_factory(max_movies_per_composer=5, json_path=movie_database_json_path)
    assert isinstance(db, MovieDatabaseFromJSON)
    assert len(db.movies) > 0  # basic sanity check


@patch("hollywood_pub_sub.movie_database_factory.MovieDatabaseFromAPI")
@patch("hollywood_pub_sub.movie_database_factory.MovieDatabaseFromAPI.tmdb_get")
def test_factory_loads_from_api(mock_tmdb_get, mock_api_class):
    mock_instance = mock_api_class.return_value

    db = movie_database_factory(max_movies_per_composer=3, api_key="fake_api_key")
    mock_api_class.assert_called_once_with(api_key="fake_api_key", max_movies_per_composer=3)
    assert db is mock_instance


def test_factory_json_path_takes_precedence_over_api_key(movie_database_json_path):
    # If both json_path and api_key provided, json_path is used
    db = movie_database_factory(
        max_movies_per_composer=10,
        json_path=movie_database_json_path,
        api_key="fake_api_key",
    )
    assert isinstance(db, MovieDatabaseFromJSON)


def test_factory_raises_without_json_or_api_key():
    with pytest.raises(ValueError, match="You must provide either a JSON path or a TMDb API key."):
        movie_database_factory(max_movies_per_composer=5)
