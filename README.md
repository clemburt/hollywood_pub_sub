# hollywood_pub_sub

# Table of Contents
- [Purpose](#purpose)
- [Installation](#installation)
- [Usage](#usage)
  - [run command](#run-command)
  - [db command](#db-command)
- [Tests](#tests)
- [Documentation](#documentation)
- [Docker Notes](#docker-notes)
- [License](#license)
- [Authors](#authors)

# Purpose
A Publisher-Subscriber simulation game between film **directors** and **composers**, using pdm and pydantic:
- a movie database is built by querying the [TMDb api](https://developer.themoviedb.org/docs/getting-started), retieving details from each movie (title, director, composer, cast, year)
- then movie announcements are randomly published: a director (publisher) tells that he is working on a movie from the database and looking for a composer
- all composers (subscribers) from the database subscribe to these announcements, and wait for a movie in which they are credited
- if that is the case, they take the assignment
- the winner is the 1st composer to secure a given number of contracts

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

Example:

```bash
[2025-07-20 21:19:59] [hollywood_pub_sub] INFO [publisher.py:62:publish] 📣 Publisher director Vittorio De Sica:
We are about to start shooting the movie Sunflower (1970)!
Who wants to score it?
[2025-07-20 21:19:59] [hollywood_pub_sub] INFO [subscriber.py:50:on_movie_published] ✋ Subscriber composer Henry Mancini:
Hi Vittorio De Sica! I will take the assignment for the movie Sunflower (1970)!
Total: 3
[2025-07-20 21:19:59] [hollywood_pub_sub] INFO [publisher.py:62:publish] 📣 Publisher director Peter Jackson:
We are about to start shooting the movie The Lord of the Rings: The Return of the King (2003)!
Who wants to score it?
[2025-07-20 21:19:59] [hollywood_pub_sub] INFO [subscriber.py:50:on_movie_published] ✋ Subscriber composer Howard Shore:
Hi Peter Jackson! I will take the assignment for the movie The Lord of the Rings: The Return of the King (2003)!
Total: 1
[2025-07-20 21:20:23] [hollywood_pub_sub] INFO [publisher.py:62:publish] 📣 Publisher director Clint Eastwood:
We are about to start shooting the movie The Bridges of Madison County (1995)!
Who wants to score it?
[2025-07-20 21:20:23] [hollywood_pub_sub] INFO [subscriber.py:50:on_movie_published] ✋ Subscriber composer Lennie Niehaus:
Hi Clint Eastwood! I will take the assignment for the movie The Bridges of Madison County (1995)!
Total: 4

[...]

[2025-07-20 21:20:24] [hollywood_pub_sub] INFO [publisher.py:62:publish] 📣 Publisher director Walter Hill:
We are about to start shooting the movie 48 Hrs. (1982)!
Who wants to score it?
[2025-07-20 21:20:24] [hollywood_pub_sub] INFO [subscriber.py:50:on_movie_published] ✋ Subscriber composer James Horner:
Hi Walter Hill! I will take the assignment for the movie 48 Hrs. (1982)!
Total: 5
[2025-07-20 21:20:24] [hollywood_pub_sub] INFO [subscriber.py:82:announce_win] 🏆 Subscriber composer James Horner has reached the winning threshold!
🎞️  Filmography:
1) Star Trek III: The Search for Spock (1984) by Leonard Nimoy
2) The Name of the Rose (1986) by Jean-Jacques Annaud
3) Titanic (1997) by James Cameron
4) Apollo 13 (1995) by Ron Howard
5) 48 Hrs. (1982) by Walter Hill
[2025-07-20 21:20:24] [hollywood_pub_sub] INFO [main.py:46:run_game] 🏆 Winner is subscriber composer James Horner with 5 movies!
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

Example:

```bash
[2025-07-21 00:11:19] [hollywood_pub_sub] INFO [main.py:86:print_composers] List of composers:
🎶 Alex North
🎶 Alexandre Desplat
🎶 Angela Morley
🎶 Arthur B. Rubinstein
🎶 Basil Poledouris
🎶 Bernard Herrmann
🎶 Bill Conti
🎶 Christopher Young
🎶 Dave Grusin

[...]

🎶 Ryuichi Sakamoto
🎶 Stephen Sondheim
🎶 Trevor Jones
🎶 Vladimir Cosma
🎶 Wojciech Kilar
```

# Tests
Run the test suite using:
```bash
pdm test
```

This will:
- Sync test dependencies
- Run all tests with coverage reporting

# Documentation
Build the sphinx documentation using
```bash
pdm doc
```

📚 [Documentation](https://clemburt.github.io/hollywood_pub_sub/)

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
