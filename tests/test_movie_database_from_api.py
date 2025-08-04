from unittest.mock import MagicMock, patch

import pytest

from hollywood_pub_sub.movie_database_from_api import MovieDatabaseFromAPI


@pytest.fixture
def fake_api_key() -> str:
    return "fake-api-key"


@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.tmdb_get")
def test_search_person_returns_valid_composer_id(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    mock_tmdb_get.return_value = {
        "results": [
            {
                "id": 555,
                "name": "Hans Zimmer",
                "known_for_department": "Music",
                "popularity": 15.0,
            },
            {
                "id": 666,
                "name": "Some Actor",
                "known_for_department": "Acting",
                "popularity": 20.0,
            },
        ]
    }
    db = MovieDatabaseFromAPI(api_key=fake_api_key, max_movies_per_composer=1, composers=["Hans Zimmer"])
    composer_id: int | None = db.search_person("Hans Zimmer")
    assert composer_id == 555


@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.tmdb_get")
def test_get_person_credits_returns_crew_dict(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    mock_tmdb_get.return_value = {"crew": [{"job": "Composer", "id": 1, "title": "Test Movie"}]}
    db = MovieDatabaseFromAPI(api_key=fake_api_key, max_movies_per_composer=1, composers=["Hans Zimmer"])
    credits = db.get_person_credits(123)
    assert isinstance(credits, dict)
    assert "crew" in credits


@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.tmdb_get")
def test_get_movie_details_extracts_director_and_cast(mock_tmdb_get: MagicMock, fake_api_key: str) -> None:
    mock_tmdb_get.return_value = {
        "title": "Inception",
        "release_date": "2010-07-16",
        "credits": {
            "cast": [
                {"name": "Leonardo DiCaprio"},
                {"name": "Joseph Gordon-Levitt"},
                {"name": "Ellen Page"},
            ],
            "crew": [
                {"job": "Director", "name": "Christopher Nolan"},
                {"job": "Producer", "name": "Emma Thomas"},
            ],
        },
    }
    db = MovieDatabaseFromAPI(api_key=fake_api_key, max_movies_per_composer=1, composers=["Hans Zimmer"])
    details = db.get_movie_details(1)
    director = db.extract_director(details)
    main_cast = db.extract_main_cast(credits=details["credits"], max_cast=3)

    assert details["title"] == "Inception"
    assert director == "Christopher Nolan"
    assert main_cast == ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"]


@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.search_person")
@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.get_person_credits")
@patch("hollywood_pub_sub.movie_database_from_api.MovieDatabaseFromAPI.get_movie_details")
def test_build_populates_movies(
    mock_get_movie_details: MagicMock,
    mock_get_person_credits: MagicMock,
    mock_search_person: MagicMock,
    fake_api_key: str,
) -> None:
    # Setup mocks
    mock_search_person.return_value = 777
    mock_get_person_credits.return_value = {
        "crew": [
            {"id": 10, "job": "Original Music Composer", "title": "Fake Movie 1"},
            {"id": 20, "job": "Composer", "title": "Fake Movie 2"},
        ]
    }
    mock_get_movie_details.side_effect = [
        {
            "title": "Fake Movie 1",
            "release_date": "2005-01-01",
            "credits": {
                "cast": [{"name": "Actor 1"}, {"name": "Actor 2"}],
                "crew": [{"job": "Director", "name": "Director 1"}],
            },
        },
        {
            "title": "Fake Movie 2",
            "release_date": "2007-02-02",
            "credits": {
                "cast": [{"name": "Actor 3"}, {"name": "Actor 4"}],
                "crew": [{"job": "Director", "name": "Director 2"}],
            },
        },
    ]

    # Instantiate after mocks are set to intercept _build calls inside __init__
    db = MovieDatabaseFromAPI(api_key=fake_api_key, max_movies_per_composer=2, composers=["Fake Composer"])

    assert len(db.movies) == 2
    assert db.movies[0].composer == "Fake Composer"
    assert db.movies[0].title == "Fake Movie 1"
    assert db.movies[1].composer == "Fake Composer"
    assert db.movies[1].title == "Fake Movie 2"
