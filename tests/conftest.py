import pytest

from main import app


@pytest.fixture(autouse=True)
def bloquear_bai_real(
    monkeypatch,
):
    """
    Testes automatizados nunca devem acessar
    a API B.AI real.
    """
    monkeypatch.setenv(
        "BAI_ENABLED",
        "0",
    )


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
    )

    with app.test_client() as test_client:
        yield test_client
