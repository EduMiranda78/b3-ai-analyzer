import pytest

from main import app


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
    )

    with app.test_client() as test_client:
        yield test_client
