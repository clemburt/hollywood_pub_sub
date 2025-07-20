# hollywood_pub_sub

# Table of Contents
- [Purpose](#purpose)
- [Installation](#installation)
- [Usage](#usage)
  - [run command](#run-command)
  - [db command](#db-command)
- [Tests](#tests)
- [Docker Notes](#docker-notes)
- [License](#license)
- [Authors](#authors)

# Purpose

A Publisher-Subscriber simulation game between film **directors** and **composers**, where movies are published and "subscribers" (composers) collect them based on their appearances in the movie list.

This project simulates a mini-event-driven system inspired by the publisher-subscriber design pattern.

# Installation
Make sure you have [PDM](https://pdm.fming.dev/) installed.

```bash
pdm install
```

If running inside Docker, you can use the published image:

```bash
docker pull ghcr.io/clemburt/hollywood_pub_sub:latest
```

# Usage
You can use the CLI either locally or from the Docker container.

## run command
Runs the full Publisher-Subscriber simulation game. The CLI will select movies for composers and publish them one by one. When a composer reaches the winning threshold (number of movies), the game stops and the winner is announced.

```bash
hollywood_pub_sub run \
  --api_key YOUR_TMDB_API_KEY \
  --max_movies_per_composer 10 \
  --winning_threshold 5
```

| Argument                    | Description                                       | Default |
| --------------------------- | ------------------------------------------------- | ------- |
| `--api_key`                 | TMDb API key (can also be set via `TMDB_API_KEY`) | `None`  |
| `--max_movies_per_composer` | Max movies to fetch per composer                  | `10`    |
| `--winning_threshold`       | Number of movies needed for a composer to win     | `5`     |

You can also run it via Docker:

```bash
docker run --rm \
  -e TMDB_API_KEY=your_key \
  ghcr.io/clemburt/hollywood_pub_sub:latest \
  hollywood_pub_sub run --max_movies_per_composer 10 --winning_threshold 5
```

## db command
Displays the list of composers used in the simulation (those the game fetches movies for).

```bash
hollywood_pub_sub db
```

Or via Docker:
```bash
docker run --rm \
  ghcr.io/clemburt/hollywood_pub_sub:latest \
  hollywood_pub_sub db
```

# Tests
Run the test suite using:
```bash
pdm test
```

This will:
- Sync test dependencies
- Run all tests with coverage reporting

# Docker Notes
The image installs only production dependencies (--prod), so tests must be run explicitly with dev install:

```bash
docker run --rm \
  -e TMDB_API_KEY=your_key \
  ghcr.io/clemburt/hollywood_pub_sub:latest \
  sh -c "pdm install -G test && pdm test"
```

# License
MIT License

# Authors
- [BURTSCHER Clément](https://github.com/clemburt)
