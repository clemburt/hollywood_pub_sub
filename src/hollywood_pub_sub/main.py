import os
import random
import time
import argparse
from typing import Optional

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie_database import MovieDatabase
from hollywood_pub_sub.publisher import Publisher
from hollywood_pub_sub.subscriber import Subscriber
from hollywood_pub_sub.settings import ComposerSettings


def run_game(
    api_key: Optional[str],
    max_movies_per_composer: int,
    winning_threshold: int,
) -> None:
    """
    Run the Publisher-Subscriber movie game simulation.

    The game fetches movies associated with composers, publishes them one by one,
    and subscribers (composers) collect movies. When a subscriber reaches the winning
    threshold, the game ends and announces the winner.

    Parameters
    ----------
    api_key : Optional[str]
        TMDb API key used to fetch movie data. If None, will look for the
        'TMDB_API_KEY' environment variable.
    max_movies_per_composer : int
        Maximum number of movies to fetch per composer.
    winning_threshold : int
        Number of collected movies a subscriber must reach to win.

    Returns
    -------
    None
    """
    # Retrieve API key from environment if not provided explicitly
    if api_key is None:
        api_key = os.getenv("TMDB_API_KEY")
        if api_key is None:
            logger.error("TMDB API key must be provided via argument or environment variable.")
            exit(1)

    # Initialize movie database and shuffle movie list
    movie_db = MovieDatabase(api_key=api_key, max_movies_per_composer=max_movies_per_composer)
    random.shuffle(movie_db.movies)

    # Create publisher and subscribers
    publisher = Publisher(movies=movie_db.movies)
    subscribers = [
        Subscriber(name=composer, winning_threshold=winning_threshold)
        for composer in movie_db.COMPOSERS
    ]

    # Subscribers subscribe to publisher's movie announcements
    for subscriber in subscribers:
        publisher.subscribe(subscriber.on_movie_published)

    logger.info("🚀 Starting publishing announcements for new movies...\n")

    # Publish movies one by one, checking if any subscriber wins
    for movie in movie_db.movies:
        publisher.publish(movie)
        time.sleep(0.5)  # Small delay to simulate event timing
        winners = [s for s in subscribers if s.has_won()]
        if winners:
            winner = winners[0]
            logger.info(f"🏆 Winner is subscriber composer {winner.name} with {winner.movies_count} movies!")
            break
    else:
        logger.info("👎 No winner reached the threshold.")


def print_composers() -> None:
    """
    Print the list of composers from the movie database.

    Returns
    -------
    None
    """
    composers = ComposerSettings().composers
    logger.info("List of composers:\n" + "\n".join(f"🎶 {composer}" for composer in composers))


def main() -> None:
    """
    Main entry point for the CLI application.

    Parses command line arguments and dispatches commands:
    - 'run': runs the movie game simulation.
    - 'db': prints the list of composers.

    Returns
    -------
    None
    """
    parser = argparse.ArgumentParser(description="Hollywood Publisher-Subscriber CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define 'run' subcommand and its arguments
    run_parser = subparsers.add_parser("run", help="Run the movie game")
    run_parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="TMDb API key (or set TMDB_API_KEY env var)",
    )
    run_parser.add_argument(
        "--max_movies_per_composer",
        type=int,
        default=10,
        help="Max movies per composer",
    )
    run_parser.add_argument(
        "--winning_threshold",
        type=int,
        default=5,
        help="Winning threshold",
    )

    # Define 'db' subcommand for printing composers
    subparsers.add_parser("db", help="Print list of composers")

    args = parser.parse_args()

    if args.command == "run":
        run_game(args.api_key, args.max_movies_per_composer, args.winning_threshold)
    elif args.command == "db":
        print_composers()


if __name__ == "__main__":
    main()
