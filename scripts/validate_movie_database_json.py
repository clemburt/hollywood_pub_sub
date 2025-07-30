import sys
from pathlib import Path

from hollywood_pub_sub.movie_database_from_json import MovieDatabaseFromJSON


def main():
    path = Path("src/hollywood_pub_sub/movie_database.json")
    try:
        MovieDatabaseFromJSON.from_json(path)
        print(f"✅ {path} is valid.")
    except Exception as e:
        print(f"❌ Validation failed for {path}:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
