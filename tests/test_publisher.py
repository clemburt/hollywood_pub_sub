from hollywood_pub_sub.publisher import Publisher
from hollywood_pub_sub.movie import Movie


def test_subscribe_and_publish(monkeypatch):
    """
    Test that subscribing a callback registers it,
    and publishing a movie calls the callback exactly once with the correct movie.
    """
    # Create a sample movie instance
    movie = Movie(
        title="Inception",
        director="Christopher Nolan",
        composer="Hans Zimmer",
        cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
        year=2010
    )
    # Initialize publisher with a list containing the movie
    publisher = Publisher(movies=[movie])

    # Dictionary to track callback invocation count and last received movie
    called = {"count": 0, "last_movie": None}

    # Define a subscriber callback function
    def callback(m: Movie):
        called["count"] += 1
        called["last_movie"] = m

    # Subscribe the callback function to the publisher
    publisher.subscribe(callback)

    # Publish the movie to all subscribers (should call the callback)
    publisher.publish(movie)

    # Assert callback was called exactly once
    assert called["count"] == 1

    # Assert callback received the correct movie object
    assert called["last_movie"] == movie


def test_publish_multiple_subscribers():
    """
    Test that multiple subscribers receive the published movie notification,
    and that their callbacks are called in the order they were subscribed.
    """
    movie = Movie(
        title="The Dark Knight",
        director="Christopher Nolan",
        composer="Hans Zimmer",
        cast=["Christian Bale", "Heath Ledger"],
        year=2008
    )
    publisher = Publisher(movies=[movie])

    # List to record the order and titles received by callbacks
    calls = []

    # Define two subscriber callback functions that append to calls list
    def cb1(m):
        calls.append(("cb1", m.title))

    def cb2(m):
        calls.append(("cb2", m.title))

    # Subscribe both callbacks
    publisher.subscribe(cb1)
    publisher.subscribe(cb2)

    # Publish the movie to all subscribers
    publisher.publish(movie)

    # Assert both callbacks were called
    assert len(calls) == 2

    # Assert callbacks were called in the order they were subscribed with correct movie titles
    assert calls == [("cb1", "The Dark Knight"), ("cb2", "The Dark Knight")]


def test_no_subscribers_publish():
    """
    Test that publishing a movie when there are no subscribers
    does not raise an error or exception.
    """
    movie = Movie(
        title="Interstellar",
        director="Christopher Nolan",
        composer="Hans Zimmer",
        cast=["Matthew McConaughey", "Anne Hathaway"],
        year=2014
    )
    publisher = Publisher(movies=[movie])

    # Call publish with no subscribers — should run silently without errors
    publisher.publish(movie)
