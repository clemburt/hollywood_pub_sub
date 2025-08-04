"""Module defining MovieDatabaseFromAPI for fetching and building a movie database from TMDb API."""

import time

from pydantic import Field, PositiveInt
import requests

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.movie_database import MovieDatabase
from hollywood_pub_sub.settings import ComposerSettings


class MovieDatabaseFromAPI(MovieDatabase):
    """
    Fetches movies from the TMDb API for a list of specified composers.

    Parameters
    ----------
    api_key : str
        TMDb API key used for authenticating API requests.
    max_movies_per_composer : PositiveInt
        Maximum number of movies to fetch per composer.
    composers : List[str], optional
        List of composer names to fetch movies for.
        Defaults to the list from ComposerSettings().

    Attributes
    ----------
    api_key : str
        TMDb API key.
    max_movies_per_composer : PositiveInt
        Maximum number of movies to fetch per composer.
    composers : List[str]
        List of composers to fetch.
    BASE_URL : str
        Base URL for TMDb API.
    _movies : List[Movie]
        Internal list of fetched movies.

    """

    api_key: str = Field(..., description="TMDb API key")
    max_movies_per_composer: PositiveInt = Field(..., description="Max movies to fetch per composer")
    composers: list[str] = Field(default_factory=lambda: ComposerSettings().composers)

    BASE_URL: str = "https://api.themoviedb.org/3"

    def __init__(self, **data):
        """
        Initialize MovieDatabaseFromAPI instance and build movie list.

        Parameters
        ----------
        **data : dict
            Initialization parameters including api_key, max_movies_per_composer, and optionally composers.

        """
        super().__init__(**data)
        self._movies = []
        self._build()

    @property
    def movies(self) -> list[Movie]:
        """
        List of fetched Movie instances.

        Returns
        -------
        List[Movie]
            The list of Movie objects fetched from the TMDb API.

        """
        return self._movies

    def _build(self) -> None:
        """
        Fetch movies from TMDb API for all composers and populate internal movie list.

        Raises
        ------
        ValueError
            If the composers list is empty.

        """
        if not self.composers:
            raise ValueError("Composers list must be set before calling _build()")

        seen_ids: set[int] = set()
        for composer in self.composers:
            logger.info(f"🎼 Fetching movies for composer: {composer}")
            composer_id: int | None = self.search_person(composer)
            if composer_id is None:
                logger.warning(f"⚠️ No ID found for composer {composer}")
                continue

            credits = self.get_person_credits(composer_id)
            crew = credits.get("crew", [])

            film_credits = [
                credit for credit in crew if credit.get("job") in ("Original Music Composer", "Music", "Composer")
            ][: self.max_movies_per_composer]

            for credit in film_credits:
                movie_id = credit["id"]
                if movie_id in seen_ids:
                    continue

                try:
                    details = self.get_movie_details(movie_id)
                    seen_ids.add(movie_id)

                    movie = Movie(
                        title=details.get("title", "Unknown"),
                        director=self.extract_director(details),
                        composer=composer,
                        cast=self.extract_main_cast(
                            credits=details.get("credits", {}),
                            max_cast=self.max_movies_per_composer,
                        ),
                        year=(int(details["release_date"][:4]) if details.get("release_date") else None),
                    )
                    self._movies.append(movie)
                    logger.info(f"✅ Added movie: {movie.title}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch movie {movie_id}: {e}")

                time.sleep(0.25)  # Rate limit pause

    def tmdb_get(self, endpoint: str, params: dict[str, str | int]) -> dict:
        """
        Send a GET request to TMDb API.

        Parameters
        ----------
        endpoint : str
            API endpoint path (e.g., "/search/person").
        params : dict
            Query parameters for the request.

        Returns
        -------
        dict
            Parsed JSON response from the API.

        Raises
        ------
        requests.HTTPError
            If the HTTP request returned an unsuccessful status code.

        """
        params["api_key"] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def search_person(self, name: str) -> int | None:
        """
        Search for a person by name and return their TMDb ID if they are a music department member.

        Parameters
        ----------
        name : str
            Name of the person to search.

        Returns
        -------
        Optional[int]
            TMDb person ID if found, else None.

        """
        data = self.tmdb_get("/search/person", {"query": name})
        results = data.get("results", [])
        music_departments = {"Sound", "Music", "Music Department"}
        candidates = [p for p in results if p.get("known_for_department") in music_departments]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.get("popularity", 0))["id"]

    def get_person_credits(self, person_id: int) -> dict:
        """
        Retrieve movie credits for a given person.

        Parameters
        ----------
        person_id : int
            TMDb person ID.

        Returns
        -------
        dict
            Dictionary containing movie credits data.

        """
        return self.tmdb_get(f"/person/{person_id}/movie_credits", {})

    def get_movie_details(self, movie_id: int) -> dict:
        """
        Retrieve detailed movie information including credits.

        Parameters
        ----------
        movie_id : int
            TMDb movie ID.

        Returns
        -------
        dict
            Dictionary containing detailed movie information.

        """
        return self.tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits"})

    def extract_director(self, details: dict) -> str:
        """
        Extract the director's name from movie details.

        Parameters
        ----------
        details : dict
            Movie details including credits.

        Returns
        -------
        str
            Director's name, or "Unknown" if not found.

        """
        crew = details.get("credits", {}).get("crew", [])
        directors = [member["name"] for member in crew if member.get("job") == "Director"]
        return directors[0] if directors else "Unknown"

    def extract_main_cast(self, credits: dict, max_cast: int) -> list[str]:
        """
        Extract the main cast members from movie credits.

        Parameters
        ----------
        credits : dict
            Movie credits dictionary.
        max_cast : int, optional
            Maximum number of cast members to extract.

        Returns
        -------
        List[str]
            List of main cast member names.

        """
        cast_list = credits.get("cast", [])[:max_cast]
        return [member["name"] for member in cast_list]
