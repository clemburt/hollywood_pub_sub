import os
import random
import time
import argparse
from typing import Optional

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie_database import MovieDatabase
from hollywood_pub_sub.publisher import Publisher
from hollywood_pub_sub.subscriber import Subscriber


def main(
    api_key: Optional[str],
    max_movies_per_composer: int = 10,
    winning_threshold: int = 5,
) -> None:
    """
    Run the Publisher-Subscriber movie game with configurable parameters.

    Parameters
    ----------
    api_key : Optional[str]
        TMDb API key to fetch movies. If None, must be set via environment variable.
    max_movies_per_composer : int, optional
        Maximum number of movies to fetch per composer (default is 10).
    winning_threshold : int, optional
        Number of movies a subscriber must count to win (default is 5).

    Returns
    -------
    None
    """
    # Use the environment variable if api_key is not provided
    if api_key is None:
        api_key = os.getenv("TMDB_API_KEY")
        if api_key is None:
            logger.error("TMDB API key must be provided via argument or environment variable.")
            return

    # Step 1: Build movie database from TMDb API with given parameters
    movie_db = MovieDatabase(
        api_key=api_key,
        max_movies_per_composer=max_movies_per_composer,
    )
    
    # Shuffle the movies randomly to vary the publishing order
    random.shuffle(movie_db.movies)

    # Step 2: Initialize the Publisher with the fetched movie list
    publisher = Publisher(movies=movie_db.movies)

    # Step 3: Create Subscribers, one per composer in the movie database
    subscribers = [
        Subscriber(
            name=composer,
            winning_threshold=winning_threshold,
        )
        for composer in movie_db.COMPOSERS
    ]

    # Step 4: Subscribe all subscribers to the publisher's notifications
    for subscriber in subscribers:
        publisher.subscribe(subscriber.on_movie_published)

    logger.info("🚀 Starting publishing announcements for new movies...\n")

    # Step 5: Publishing loop - publish one movie every 0.5 seconds
    for movie in movie_db.movies:
        publisher.publish(movie)
        time.sleep(0.5)

        # Step 6: Check if any subscriber has reached the winning threshold
        winners = [subscriber for subscriber in subscribers if subscriber.has_won()]
        if winners:
            winner = winners[0]
            logger.info(f"🏆 Winner is subscriber composer {winner.name} with {winner.movies_count} movies!")
            break
    else:
        # No winner after publishing all movies
        logger.info("👎 No winner reached the threshold.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Publisher-Subscriber movie game.")
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="TMDb API key. If not set, will look for TMDB_API_KEY environment variable.",
    )
    parser.add_argument(
        "--max_movies_per_composer",
        type=int,
        default=10,
        help="Maximum number of movies to fetch per composer (default: 10).",
    )
    parser.add_argument(
        "--winning_threshold",
        type=int,
        default=5,
        help="Number of movies a subscriber must count to win (default: 5).",
    )
    args = parser.parse_args()

    main(
        api_key=args.api_key,
        max_movies_per_composer=args.max_movies_per_composer,
        winning_threshold=args.winning_threshold,
    )
