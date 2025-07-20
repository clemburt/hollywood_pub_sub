from typing import Callable, List

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie import Movie

class Publisher:
    """
    Publisher class that publishes movies to subscribers.

    Attributes
    ----------
    name : str
        Name of the publisher.
    movies : List[Movie]
        List of Movie instances to publish.
    subscribers : List[Callable[[Movie], None]]
        List of subscriber callback functions.

    Methods
    -------
    subscribe(callback: Callable[[Movie], None]) -> None
        Register a subscriber callback to receive published movies.
    publish(movie: Movie) -> None
        Publish a movie to all subscribers by calling their callbacks.
    """

    def __init__(self, movies: List[Movie]):
        """
        Initialize Publisher.

        Parameters
        ----------
        name : str
            Name of the publisher.
        movies : List[Movie]
            List of Movie instances to be published.
        """
        self.movies = movies
        self.subscribers: List[Callable[[Movie], None]] = []

    def subscribe(self, callback: Callable[[Movie], None]) -> None:
        """
        Subscribe a callback function to the publisher.

        Parameters
        ----------
        callback : Callable[[Movie], None]
            Function to be called when a movie is published.
            It should accept a single argument: the Movie instance.
        """
        self.subscribers.append(callback)

    def publish(self, movie: Movie) -> None:
        """
        Publish a movie to all subscribers.

        Parameters
        ----------
        movie : Movie
            Movie instance to publish.
        """
        logger.info(f"📣 Publisher director {movie.director} is looking for a composer for his film {movie.title} ({movie.year})")
        for callback in self.subscribers:
            callback(movie)
