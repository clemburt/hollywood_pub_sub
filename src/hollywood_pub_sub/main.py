import argparse
import os
import random
import time
from pathlib import Path
from typing import Optional

from pydantic import FilePath

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie_database_factory import movie_database_factory
from hollywood_pub_sub.publisher import Publisher
from hollywood_pub_sub.settings import ComposerSettings
from hollywood_pub_sub.subscriber import Subscriber


def run_game(
    json_path: Optional[FilePath] = None,
    api_key: Optional[str] = os.getenv("TMDB_API_KEY"),
    max_movies_per_composer: Optional[int] = 5,
    winning_threshold: Optional[int] = 3,
) -> None:
    """
    Run the Publisher-Subscriber movie game simulation.

    Parameters
    ----------
    json_path : FilePath, optional
        Path to a local JSON file to load movies from. If provided, overrides API.
    api_key : str, optional
        TMDb API key. Used only if `json_path` is not provided. Defaults to environment variable TMDB_API_KEY.
    max_movies_per_composer : int, optional
        Maximum number of movies to fetch per composer from the API. Defaults to 5.
    winning_threshold : int, optional
        Number of collected movies needed by a subscriber to win. Defaults to 3.
    """
    if json_path is None and api_key is None:
        logger.error(
            "❌ You must provide either --json_path or --api_key (or set TMDB_API_KEY)."
        )
        exit(1)

    movie_db = movie_database_factory(
        max_movies_per_composer=max_movies_per_composer,
        api_key=api_key,
        json_path=json_path,
    )

    random.shuffle(movie_db.movies)

    publisher = Publisher(movies=movie_db.movies)
    subscribers = [
        Subscriber(name=composer, winning_threshold=winning_threshold)
        for composer in movie_db.composers
    ]

    for subscriber in subscribers:
        publisher.subscribe(subscriber.on_movie_published)

    logger.info("🚀 Starting publishing announcements for new movies...\n")

    for movie in movie_db.movies:
        publisher.publish(movie)
        time.sleep(0.5)

        winners = [s for s in subscribers if s.has_won()]
        if winners:
            winner = winners[0]
            logger.info(
                f"🏆 Winner is subscriber composer {winner.name} with {winner.movies_count} movies!"
            )
            break
    else:
        logger.info("👎 No winner reached the threshold.")


def print_composers() -> None:
    """
    Print the list of composers from ComposerSettings.
    """
    composers = ComposerSettings().composers
    logger.info(
        "List of composers:\n" + "\n".join(f"🎶 {composer}" for composer in composers)
    )


def main() -> None:
    """
    Main CLI entry point.

    Handles:
    - 'run': run the Publisher-Subscriber movie game
    - 'db': list available composers
    """
    parser = argparse.ArgumentParser(
        description="🎬 Hollywood Publisher-Subscriber CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the movie game")
    run_parser.add_argument(
        "--api_key", type=str, help="TMDb API key (or set TMDB_API_KEY env var)"
    )
    run_parser.add_argument(
        "--json_path", type=str, help="Path to a JSON file with preloaded movies"
    )
    run_parser.add_argument(
        "--max_movies_per_composer",
        type=int,
        default=5,
        help="Maximum movies per composer (API)",
    )
    run_parser.add_argument(
        "--winning_threshold",
        type=int,
        default=3,
        help="Movies needed by a subscriber to win",
    )

    subparsers.add_parser("db", help="Print list of composers")

    args = parser.parse_args()

    if args.command == "run":
        validated_path: Optional[FilePath] = None
        if args.json_path:
            path_obj = Path(args.json_path).expanduser().resolve()
            if not path_obj.exists() or not path_obj.is_file():
                logger.error(
                    f"❌ JSON path does not exist or is not a file: {path_obj}"
                )
                exit(1)
            validated_path = FilePath(path_obj)

        run_game(
            max_movies_per_composer=args.max_movies_per_composer,
            winning_threshold=args.winning_threshold,
            json_path=validated_path,
            api_key=args.api_key,
        )

    elif args.command == "db":
        print_composers()


if __name__ == "__main__":
    main()
