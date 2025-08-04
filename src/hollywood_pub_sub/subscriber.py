"""Subscriber module handling the Subscriber class that listens to published movies and tracks wins."""

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie import Movie


class Subscriber:
    """
    Subscriber class that listens to published movies and tracks the number of movies composed by its composer name.

    Attributes
    ----------
    name : str
        Name of the subscriber (composer name).
    movies_count : int
        Number of movies received for this subscriber's composer.
    winning_threshold : int
        Number of movies required to declare this subscriber as winner.
    movies_won : list[Movie]
        List of movies assigned to the composer.

    """

    def __init__(self, name: str, winning_threshold: int):
        """Initialize a Subscriber."""
        self.name = name
        self.movies_count = 0
        self.winning_threshold = winning_threshold
        self.movies_won: list[Movie] = []

    def on_movie_published(self, movie: Movie) -> None:
        """
        Invoke callback when a movie is published.

        Parameters
        ----------
        movie : Movie
            Published movie object.

        """
        if movie.composer == self.name:
            self.movies_count += 1
            self.movies_won.append(movie)
            logger.info(
                f"✋ Subscriber composer {self.name}:\n"
                f"Hi {movie.director}! I will take the assignment for the movie {movie.title} ({movie.year})!\n"
                f"Total: {self.movies_count}"
            )
            if self.has_won():
                self.announce_win()

    def has_won(self) -> bool:
        """Return True if movies_count >= winning_threshold, else False."""
        return self.movies_count >= self.winning_threshold

    def announce_win(self) -> None:
        """Announce the subscriber as winner and print their movie track record."""
        filmography_lines = [
            f"{idx}) {movie.title} ({movie.year}) by {movie.director}"
            for idx, movie in enumerate(self.movies_won, start=1)
        ]
        filmography_block = (
            f"🏆 Subscriber composer {self.name} has reached the winning threshold!\n"
            "🎞️  Filmography:\n" + "\n".join(filmography_lines)
        )
        logger.info(filmography_block)
