import logging
import pytest

@pytest.fixture(autouse=True, scope="session")
def disable_urllib3_debug_logging():
    """Disable DEBUG logging from urllib3 during tests to reduce noise."""
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    yield
