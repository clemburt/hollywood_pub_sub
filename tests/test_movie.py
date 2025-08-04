"""Tests for the Movie model validation and creation."""

from pydantic import ValidationError
import pytest

from hollywood_pub_sub.movie import Movie


def test_movie_creation_success():
    """Test successful creation of a Movie instance with valid data."""
    movie = Movie(
        title="The Matrix",
        director="The Wachowskis",
        composer="Don Davis",
        cast=["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
        year=1999,
    )
    assert movie.title == "The Matrix"
    assert movie.director == "The Wachowskis"
    assert movie.composer == "Don Davis"
    assert movie.cast == ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"]
    assert movie.year == 1999


def test_movie_cast_must_be_list_of_strings():
    """Test that cast must be a list of strings. Passing invalid types raises ValidationError."""
    # cast with non-string element should raise an error
    with pytest.raises(ValidationError):
        Movie(
            title="Invalid Cast",
            director="Some Director",
            composer="Some Composer",
            cast=["Actor 1", 123, "Actor 3"],  # 123 is invalid
            year=2020,
        )


def test_movie_required_fields():
    """Test that required fields must be present. Omitting any raises ValidationError."""
    # Missing title
    with pytest.raises(ValidationError):
        Movie(
            director="Director",
            composer="Composer",
            cast=["Actor A", "Actor B"],
            year=2000,
        )

    # Missing director
    with pytest.raises(ValidationError):
        Movie(title="Title", composer="Composer", cast=["Actor A", "Actor B"], year=2000)

    # Missing composer
    with pytest.raises(ValidationError):
        Movie(title="Title", director="Director", cast=["Actor A", "Actor B"], year=2000)

    # Missing cast
    with pytest.raises(ValidationError):
        Movie(title="Title", director="Director", composer="Composer", year=2000)


def test_movie_year_must_be_int_or_none():
    """Test that year must be an int or None. Invalid types raise ValidationError."""
    with pytest.raises(ValidationError):
        Movie(
            title="Bad Year",
            director="Director",
            composer="Composer",
            cast=["Actor 1"],
            year="Not a year",  # invalid type
        )
