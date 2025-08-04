from pydantic import ValidationError
import pytest

from hollywood_pub_sub.movie import Movie


def test_movie_creation_success():
    """
    Test that a Movie instance can be successfully created
    with all required fields and valid data.
    """
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
    """
    Test that the cast attribute must be a list of strings.
    Passing invalid types should raise a ValidationError.
    """
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
    """
    Test that all required fields (title, director, composer, cast) must be present.
    Omitting any required field should raise ValidationError.
    """
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
    """
    Test that year must be either an int or omitted (None).
    Passing invalid type should raise a ValidationError.
    """
    with pytest.raises(ValidationError):
        Movie(
            title="Bad Year",
            director="Director",
            composer="Composer",
            cast=["Actor 1"],
            year="Not a year",  # invalid type
        )
