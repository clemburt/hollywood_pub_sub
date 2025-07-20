import os
import random
import time
from typing import Optional

import typer

from hollywood_pub_sub.logger import logger
from hollywood_pub_sub.movie_database import MovieDatabase
from hollywood_pub_sub.publisher import Publisher
from hollywood_pub_sub.subscriber import Subscriber

app = typer.Typer()


def run_game(
    api_key: Optional[str] = typer.Option(
        None, help="TMDb API key (or set TMDB_API_KEY env var)"
    ),
    max_movies_per_composer: int = typer.Option(10, help="Max movies per composer"),
    winning_threshold: int = typer.Option(5, help="Winning threshold"),
):
    """
    Run the Publisher-Subscriber movie game.
    """
    if api_key is None:
        api_key = os.getenv("TMDB_API_KEY")
        if api_key is None:
            logger.error("TMDB API key must be provided via argument or environment variable.")
            raise typer.Exit(code=1)

    movie_db = MovieDatabase(api_key=api_key, max_movies_per_composer=max_movies_per_composer)
    random.shuffle(movie_db.movies)
    publisher = Publisher(movies=movie_db.movies)
    subscribers = [
        Subscriber(name=composer, winning_threshold=winning_threshold)
        for composer in movie_db.COMPOSERS
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
            logger.info(f"🏆 Winner is subscriber composer {winner.name} with {winner.movies_count} movies!")
            break
    else:
        logger.info("👎 No winner reached the threshold.")


@app.command()
def run(
    api_key: Optional[str] = typer.Option(
        None, help="TMDb API key (or set TMDB_API_KEY env var)"
    ),
    max_movies_per_composer: int = typer.Option(10, help="Max movies per composer"),
    winning_threshold: int = typer.Option(5, help="Winning threshold"),
):
    run_game(api_key, max_movies_per_composer, winning_threshold)


@app.command()
def db():
    """
    Print the list of composers from the movie database.
    """
    api_key = os.getenv("TMDB_API_KEY", "")
    movie_db = MovieDatabase(api_key=api_key)
    logger.info("List of composers:\n" + "\n".join(f"🎶 {composer}" for composer in movie_db.COMPOSERS))



if __name__ == "__main__":
    app()
