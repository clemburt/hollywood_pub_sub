import json
import tempfile
from pathlib import Path

import pytest

from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.movie_database import MovieDatabase


# Concrete subclass for testing - not named Test* to avoid pytest collection
class ConcreteMovieDatabase(MovieDatabase):
    def __init__(self, movies):
        super().__init__()
        self._movies = movies

    @property
    def movies(self):
        return self._movies


@pytest.fixture
def sample_movies():
    return [
        Movie(
            title="Inception",
            director="Christopher Nolan",
            composer="Hans Zimmer",
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            year=2010,
        ),
        Movie(
            title="Interstellar",
            director="Christopher Nolan",
            composer="Hans Zimmer",
            cast=["Matthew McConaughey", "Anne Hathaway"],
            year=2014,
        ),
        Movie(
            title="The Dark Knight",
            director="Christopher Nolan",
            composer="Hans Zimmer",
            cast=["Christian Bale", "Heath Ledger"],
            year=2008,
        ),
        Movie(
            title="Pulp Fiction",
            director="Quentin Tarantino",
            composer="Various",
            cast=["John Travolta", "Samuel L. Jackson"],
            year=1994,
        ),
    ]


@pytest.fixture
def movie_db(sample_movies):
    return ConcreteMovieDatabase(movies=sample_movies)


def test_filter_by_title(movie_db):
    filtered = movie_db.filter(title="Inception")
    assert len(filtered) == 1
    assert filtered[0].title == "Inception"


def test_filter_by_director(movie_db):
    filtered = movie_db.filter(director="Christopher Nolan")
    assert len(filtered) == 3
    assert all(movie.director == "Christopher Nolan" for movie in filtered)


def test_filter_by_composer(movie_db):
    filtered = movie_db.filter(composer="Hans Zimmer")
    assert len(filtered) == 3
    assert all(movie.composer == "Hans Zimmer" for movie in filtered)


def test_filter_by_year(movie_db):
    filtered = movie_db.filter(year=2014)
    assert len(filtered) == 1
    assert filtered[0].year == 2014


def test_filter_by_cast_single_actor(movie_db):
    filtered = movie_db.filter(cast="Leonardo DiCaprio")
    assert len(filtered) == 1
    assert "Leonardo DiCaprio" in filtered[0].cast


def test_filter_by_cast_multiple_actors(movie_db):
    filtered = movie_db.filter(cast=["John Travolta", "Samuel L. Jackson"])
    assert len(filtered) == 1
    assert all(
        actor in filtered[0].cast for actor in ["John Travolta", "Samuel L. Jackson"]
    )


def test_filter_combined_criteria(movie_db):
    filtered = movie_db.filter(
        director="Christopher Nolan", composer="Hans Zimmer", year=2008
    )
    assert len(filtered) == 1
    assert filtered[0].title == "The Dark Knight"


def test_filter_no_match(movie_db):
    filtered = movie_db.filter(title="Nonexistent Movie")
    assert filtered == []


def test_to_json_returns_string(movie_db):
    json_str = movie_db.to_json()
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == len(movie_db.movies)
    assert data[0]["title"] == movie_db.movies[0].title


def test_to_json_writes_to_file(movie_db):
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / "movies.json"
        result = movie_db.to_json(path=path)
        assert result is None  # When path provided, should return None

        # Read file and verify content
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert isinstance(data, list)
        assert len(data) == len(movie_db.movies)
        assert data[0]["title"] == movie_db.movies[0].title
