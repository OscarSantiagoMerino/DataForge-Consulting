import pytest

from finbank.sample import generate_sample


@pytest.fixture
def sample():
    return generate_sample(n_clients=2000, seed=7)
