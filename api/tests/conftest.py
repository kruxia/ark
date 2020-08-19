import os
import pytest
from starlette.testclient import TestClient
from api.main import app


@pytest.fixture(scope="session")
def setup():
    os.environ['ARK_TEST_PREFIX'] = '__ARK_TEST.'
    yield


@pytest.fixture()
def client(setup):
    return TestClient(app)
