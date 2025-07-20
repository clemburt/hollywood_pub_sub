from typing import List, Dict, Optional, Union
from pathlib import Path
import time
import json
import requests

from pydantic import BaseModel, Field, model_validator

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.settings import ComposerSettings


class MovieDatabase(BaseModel):
    """
    Movie database builder that either loads data from a JSON file
    or fetches it from TMDb (The Movie Database) based on a list of composers.

    Parameters
    ----------
    api_key : Optional[str]
        API key for TMDb (required only if no JSON file path is given).
    json_path : Optional[Union[str, Path]]
        Optional path to a JSON file to load movies from instead of fetching from TMDb.

    Attributes
    ----------
    COMPOSERS : List[str]
        A predefined list of film composers whose movies will be fetched from TMDb.
    movies : List[Movie]
        List of Movie objects representing the movies loaded or fetched.
    max_movies_per_composer : int
        Maximum number of movies to fetch per composer from TMDb.
    BASE_URL : str
        Base URL for TMDb API requests.
    """

    api_key: Optional[str] = None
    json_path: Optional[Union[str, Path]] = None
    BASE_URL: str = "https://api.themoviedb.org/3"

    COMPOSERS: List[str] = Field(default_factory=lambda: ComposerSettings().composers)

    movies: List[Movie] = Field(default_factory=list)
    max_movies_per_composer: int = Field(default=5)

    @model_validator(mode="after")
    def initialize_movies(self) -> "MovieDatabase":
        """
        Initialize the `movies` attribute by loading from a JSON file or
        fetching movie data from the TMDb API.

        Returns
        -------
        MovieDatabase
            The validated and initialized MovieDatabase instance.
        """
        if self.json_path:
            self._load_movies_from_json(self.json_path)
        elif self.api_key:
            self._fetch_movies_from_api()
        else:
            raise ValueError("You must provide either a JSON path or a valid TMDb API key.")
        return self

    def _load_movies_from_json(self, path: Union[str, Path]) -> None:
        """
        Load movie data from a local JSON file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the JSON file containing movie data.
        """
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"❌ File not found: {path}")

        logger.info(f"📁 Loading movies from JSON: {path}")
        with path.open("r", encoding="utf-8") as f:
            data: List[dict] = json.load(f)

        self.movies = [Movie(**entry) for entry in data]
        logger.info(f"✅ Loaded {len(self.movies)} movies from JSON.")

    def _fetch_movies_from_api(self) -> None:
        """
        Fetch movies from the TMDb API for each composer in the list
        and populate the `movies` attribute.

        Notes
        -----
        - Limits the number of movies fetched per composer to `max_movies_per_composer`.
        - Skips duplicates and handles API exceptions gracefully.
        """
        seen_ids: set[int] = set()

        for composer in self.COMPOSERS:
            logger.info(f"🎼 Fetching movies for composer: {composer}")
            composer_id = self.search_person(composer)
            if not composer_id:
                logger.warning(f"⚠️ No ID found for composer {composer}")
                continue

            credits = self.get_person_credits(composer_id)
            crew = credits.get("crew", [])
            film_credits = [
                m for m in crew
                if m.get("job") in ("Original Music Composer", "Music", "Composer")
            ][:self.max_movies_per_composer]

            for credit in film_credits:
                movie_id = credit["id"]
                if movie_id in seen_ids:
                    continue

                try:
                    details = self.get_movie_details(movie_id)
                    seen_ids.add(movie_id)

                    self.movies.append(Movie(
                        title=details.get("title", "Unknown"),
                        director=self._extract_director(details),
                        composer=composer,
                        cast=self.extract_main_cast(details.get("credits", {})),
                        year=int(details["release_date"][:4]) if "release_date" in details else None
                    ))

                    logger.info(f"✅ Added: {details.get('title')}")

                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch movie {movie_id}: {e}")

                # Be kind to the API: rate-limiting
                time.sleep(0.25)

    def _extract_director(self, details: dict) -> str:
        """
        Extract the director's name from the movie credits.

        Parameters
        ----------
        details : dict
            Movie details with embedded credits.

        Returns
        -------
        str
            The director's name or "Unknown" if not found.
        """
        directors = [
            member["name"]
            for member in details.get("credits", {}).get("crew", [])
            if member.get("job") == "Director"
        ]
        return directors[0] if directors else "Unknown"

    def tmdb_get(self, endpoint: str, params: Dict[str, str]) -> dict:
        """
        Make a GET request to the TMDb API.

        Parameters
        ----------
        endpoint : str
            The TMDb API endpoint (e.g., "/search/person").
        params : Dict[str, str]
            Query parameters to include in the request.

        Returns
        -------
        dict
            The JSON response from the API.
        """
        params["api_key"] = self.api_key
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def search_person(self, name: str) -> Optional[int]:
        """
        Search for a person by name and return their TMDb ID
        only if they are known for music-related work.

        Parameters
        ----------
        name : str
            Name of the person to search for.

        Returns
        -------
        Optional[int]
            TMDb person ID if a valid composer is found, else None.
        """
        data = self.tmdb_get("/search/person", {"query": name})
        results = data.get("results", [])

        music_departments = {"Sound", "Music", "Music Department"}
        candidates = [
            person for person in results
            if person.get("known_for_department") in music_departments
        ]

        if not candidates:
            logger.warning(f"❌ No composer found in music-related departments for: {name}")
            return None

        best_match = max(candidates, key=lambda p: p.get("popularity", 0))
        return best_match["id"]

    def get_person_credits(self, person_id: int) -> Dict:
        """
        Fetch movie credits for a given person ID.

        Parameters
        ----------
        person_id : int
            TMDb person ID.

        Returns
        -------
        Dict
            Dictionary containing the person's movie credits.
        """
        return self.tmdb_get(f"/person/{person_id}/movie_credits", {})

    def get_movie_details(self, movie_id: int) -> dict:
        """
        Fetch detailed movie information including credits.

        Parameters
        ----------
        movie_id : int
            TMDb movie ID.

        Returns
        -------
        dict
            Movie details and credits.
        """
        return self.tmdb_get(f"/movie/{movie_id}", {"append_to_response": "credits"})

    def extract_main_cast(self, credits: dict, max_cast: int = 3) -> List[str]:
        """
        Extract the top billed cast members from movie credits.

        Parameters
        ----------
        credits : dict
            Dictionary containing movie cast data.
        max_cast : int, optional
            Maximum number of cast members to return (default is 3).

        Returns
        -------
        List[str]
            List of main cast member names.
        """
        return [member["name"] for member in credits.get("cast", [])[:max_cast]]

    def export_to_json(self, path: Union[str, Path]) -> None:
        """
        Export the movie list to a JSON file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the output JSON file.
        """
        path = Path(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(
                [movie.model_dump() for movie in self.movies],
                f,
                indent=4,
                ensure_ascii=False
            )
        logger.info(f"💾 Exported {len(self.movies)} movies to {path}")


if __name__ == "__main__":
    import os
    api_key = os.getenv("TMDB_API_KEY")
    movie_db = MovieDatabase(api_key=api_key)
    logger.info(f"\n🎬 Total movies fetched: {len(movie_db.movies)}")
    for movie in movie_db.movies[:5]:
        logger.info(movie.model_dump_json(indent=4))
