"""Script to validate the movie_database.json file against the Movie schema."""

from pathlib import Path
import sys

from hollywood_pub_sub.movie_database_from_json import MovieDatabaseFromJSON


def main():
    """Validate the JSON file and print result."""
    path = Path("src/hollywood_pub_sub/movie_database.json")
    try:
        MovieDatabaseFromJSON.from_json(path)
        print(f"✅ {path} is valid.")
    except Exception as e:
        print(f"❌ Validation failed for {path}:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
