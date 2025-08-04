from hollywood_pub_sub.movie import Movie
from hollywood_pub_sub.subscriber import Subscriber


def make_movie(title="Title", composer="Composer", director="Director", year=2000):
    """
    Helper function to quickly create a Movie instance with default or given values.
    """
    return Movie(title=title, composer=composer, director=director, cast=[], year=year)


def test_on_movie_published_increments_and_stores(monkeypatch):
    """
    Test that on_movie_published increments the movie count and stores the movie correctly
    only when the composer matches the subscriber's name.
    Also test that announce_win is called when threshold is reached.
    """
    sub = Subscriber(name="Hans Zimmer", winning_threshold=2)

    # Create movies with matching and non-matching composers
    movie1 = make_movie(title="Movie 1", composer="Hans Zimmer")
    movie2 = make_movie(title="Movie 2", composer="Hans Zimmer")
    movie3 = make_movie(title="Movie 3", composer="Other Composer")

    # Replace announce_win method with a spy to check if it is called
    announce_called = {"called": False}

    def fake_announce_win():
        announce_called["called"] = True

    monkeypatch.setattr(sub, "announce_win", fake_announce_win)

    # Publish first movie with matching composer
    sub.on_movie_published(movie1)
    assert sub.movies_count == 1  # count should increase
    assert sub.movies_won == [movie1]  # movie should be stored
    assert not announce_called["called"]  # announce_win not called yet

    # Publish second movie with matching composer, should trigger announce_win
    sub.on_movie_published(movie2)
    assert sub.movies_count == 2
    assert sub.movies_won == [movie1, movie2]
    assert announce_called["called"]  # announce_win should have been called now

    # Publish movie with non-matching composer, should not affect count or list
    sub.on_movie_published(movie3)
    assert sub.movies_count == 2  # unchanged
    assert sub.movies_won == [movie1, movie2]  # unchanged


def test_has_won_behavior():
    """
    Test the has_won() method returns True only when movies_count
    is at or above the winning_threshold.
    """
    sub = Subscriber(name="John Williams", winning_threshold=3)

    # Initially, subscriber hasn't won
    assert not sub.has_won()

    # Below threshold still returns False
    sub.movies_count = 2
    assert not sub.has_won()

    # At threshold returns True
    sub.movies_count = 3
    assert sub.has_won()


def test_announce_win_logs(monkeypatch):
    """
    Test that announce_win() logs the winning message and filmography correctly.
    """
    # Create subscriber with a low winning threshold to trigger easily
    sub = Subscriber(name="Alex North", winning_threshold=1)

    # Add a sample movie to subscriber's won list
    movie = make_movie(title="Spartacus", composer="Alex North", director="Stanley Kubrick", year=1960)
    sub.movies_won.append(movie)

    logged_messages = []

    # Import the subscriber module to patch its logger
    import hollywood_pub_sub.subscriber as subscriber_module

    # Define a fake logger.info function that saves messages for assertions
    def fake_info(msg):
        logged_messages.append(msg)

    # Patch the logger.info method in the subscriber module with our fake_info
    monkeypatch.setattr(subscriber_module.logger, "info", fake_info)

    # Call announce_win, which should call logger.info internally
    sub.announce_win()

    # Check that the winning announcement message was logged
    assert any("🏆 Subscriber composer Alex North has reached the winning threshold!" in msg for msg in logged_messages)

    # Check that the filmography entry is logged correctly
    assert any("1) Spartacus (1960) by Stanley Kubrick" in msg for msg in logged_messages)
