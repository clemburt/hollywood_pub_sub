import pytest
from pathlib import Path

from hollywood_pub_sub.movie_database_from_json import MovieDatabaseFromJSON


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

@pytest.fixture
def movie_db(movie_db_json_path: Path) -> MovieDatabaseFromJSON:
    # Load the database from the JSON file using the class method
    return MovieDatabaseFromJSON.from_json(movie_db_json_path)

def test_movies_loaded(movie_db):
    # The JSON contains 25 movies
    assert len(movie_db.movies) == 25

def test_unique_composers(movie_db):
    composers = movie_db.composers
    # Check that all composers are strings and the list is sorted
    assert all(isinstance(c, str) for c in composers)
    assert composers == sorted(composers)
    # Check that known composers are present
    assert "John Williams" in composers
    assert "Michel Legrand" in composers

def test_first_movie_title(movie_db):
    # The first movie in the list should have the correct title (here: Citizen Kane)
    assert movie_db.movies[0].title == "Citizen Kane"

def test_find_movies_by_director(movie_db):
    # Manually filter movies by director
    orson_movies = [m for m in movie_db.movies if m.director == "Orson Welles"]
    titles = [m.title for m in orson_movies]
    assert "Citizen Kane" in titles
    assert "The Magnificent Ambersons" in titles
    assert len(orson_movies) == 2

def test_find_movies_by_year(movie_db):
    # Find movies released in 1983 (Michel Legrand has 2 films that year)
    movies_1983 = [m for m in movie_db.movies if m.year == 1983]
    titles = [m.title for m in movies_1983]
    assert "Yentl" in titles
    assert "A Love in Germany" in titles
    assert len(movies_1983) == 2

def test_movie_cast_contains_actor(movie_db):
    # Check that a specific actor appears in the cast of at least one movie
    actor = "Harrison Ford"
    movies_with_actor = [m for m in movie_db.movies if actor in m.cast]
    assert len(movies_with_actor) > 0
    titles = [m.title for m in movies_with_actor]
    assert "Raiders of the Lost Ark" in titles
    assert "Indiana Jones and the Last Crusade" in titles

def test_composers_property_consistency(movie_db):
    # Verify that the composers property matches the unique composers in the movies
    all_composers = set(m.composer for m in movie_db.movies)
    composers_property = set(movie_db.composers)
    assert all_composers == composers_property