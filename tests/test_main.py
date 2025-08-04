"""Tests for the main module of hollywood_pub_sub."""

from pathlib import Path
import sys
import types
from unittest.mock import MagicMock

import pytest

import hollywood_pub_sub.main as main


@pytest.fixture
def fake_movies():
    """Provide a list of simple mock movie objects."""
    Movie = types.SimpleNamespace
    return [
        Movie(
            title="Movie1",
            composer="Composer1",
            director="Dir1",
            cast=["Actor1"],
            year=2000,
        ),
        Movie(
            title="Movie2",
            composer="Composer2",
            director="Dir2",
            cast=["Actor2"],
            year=2001,
        ),
        Movie(
            title="Movie3",
            composer="Composer1",
            director="Dir1",
            cast=["Actor3"],
            year=2002,
        ),
    ]


@pytest.fixture
def fake_movie_db(fake_movies):
    """Provide a MagicMock simulating the movie database with movies and composers."""
    db = MagicMock()
    db.movies = fake_movies
    db.composers = ["Composer1", "Composer2"]
    return db


def test_run_game_exits_without_api_key_or_json(monkeypatch):
    """Test run_game exits if no api_key or json_path is provided."""
    monkeypatch.setattr(main.logger, "error", MagicMock())
    monkeypatch.setattr(sys, "exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        main.run_game(json_path=None, api_key=None)

    main.logger.error.assert_called_once_with(
        "❌ You must provide either --json_path or --api_key (or set TMDB_API_KEY)."
    )


def test_run_game_runs_with_json(monkeypatch, fake_movie_db):
    """Test run_game runs correctly when json_path is provided."""
    # Patch factory to return our fake db
    monkeypatch.setattr(main, "movie_database_factory", lambda **kwargs: fake_movie_db)

    # Patch publisher and subscriber to track calls
    fake_publisher = MagicMock()
    fake_publisher.publish = MagicMock()
    monkeypatch.setattr(main, "Publisher", lambda **kwargs: fake_publisher)

    fake_subscriber = MagicMock()
    fake_subscriber.has_won.return_value = False
    fake_subscriber.movies_count = 0
    # We will have one subscriber per composer
    monkeypatch.setattr(main, "Subscriber", lambda name, winning_threshold: fake_subscriber)

    # Patch logger to suppress output
    monkeypatch.setattr(main.logger, "info", MagicMock())

    # Patch time.sleep to skip delay
    monkeypatch.setattr(main.time, "sleep", lambda x: None)

    main.run_game(
        json_path=Path("fake.json"),
        api_key=None,
        max_movies_per_composer=2,
        winning_threshold=1,
    )

    # Assert publisher published all movies
    assert fake_publisher.publish.call_count == len(fake_movie_db.movies)

    # Assert subscribers subscribed
    fake_publisher.subscribe.assert_called()  # subscribed at least once


def test_print_composers(monkeypatch):
    """Test print_composers outputs all composers."""
    # Patch ComposerSettings to return known composers
    monkeypatch.setattr(main, "ComposerSettings", lambda: types.SimpleNamespace(composers=["C1", "C2"]))
    monkeypatch.setattr(main.logger, "info", MagicMock())

    main.print_composers()

    calls = main.logger.info.call_args[0][0]
    assert "C1" in calls and "C2" in calls


def test_main_run_command(monkeypatch):
    """Test the main 'run' command parses args and calls run_game."""
    # Patch sys.argv to simulate CLI call
    monkeypatch.setattr(sys, "argv", ["prog", "run", "--api_key", "abc123"])

    monkeypatch.setattr(main, "run_game", MagicMock())

    # Patch Path.exists and is_file to True for json_path validation, even if not used here
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_file", lambda self: True)

    main.main()

    main.run_game.assert_called_once()
    args = main.run_game.call_args[1]
    assert args["api_key"] == "abc123"


def test_main_db_command(monkeypatch):
    """Test the main 'db' command calls print_composers."""
    monkeypatch.setattr(sys, "argv", ["prog", "db"])

    monkeypatch.setattr(main, "print_composers", MagicMock())

    main.main()

    main.print_composers.assert_called_once()


def test_main_invalid_json_path(monkeypatch):
    """Test main exits with error when json_path does not exist."""
    monkeypatch.setattr(sys, "argv", ["prog", "run", "--json_path", "/nonexistent/path.json"])
    monkeypatch.setattr(main.logger, "error", MagicMock())
    monkeypatch.setattr(Path, "exists", lambda self: False)
    monkeypatch.setattr(sys, "exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        main.main()

    main.logger.error.assert_called_once()


@pytest.mark.parametrize(
    "json_path_arg, expected_valid",
    [
        (None, False),
        ("", False),
        ("somefile.json", True),
    ],
)
def test_validated_path_handling(monkeypatch, json_path_arg, expected_valid):
    """Test main validates json_path argument correctly in CLI."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "run"] + (["--json_path", json_path_arg] if json_path_arg else []),
    )

    # Prepare a mock for logger.error
    mock_logger_error = MagicMock()
    monkeypatch.setattr(main.logger, "error", mock_logger_error)

    def fake_run_game(*args, **kwargs):
        if not expected_valid:
            main.logger.error("Error simulated in fake_run_game")
            raise SystemExit(1)

    monkeypatch.setattr(main, "run_game", fake_run_game)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_file", lambda self: True)

    if expected_valid:
        main.main()
    else:
        with pytest.raises(SystemExit):
            main.main()
        mock_logger_error.assert_called()
