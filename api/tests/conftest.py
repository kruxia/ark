import asyncio
import os
import databases
import pytest
from starlette.testclient import TestClient
from api.main import app


@pytest.fixture(scope="session")
def setup():
    os.environ['ARK_TEST_PREFIX'] = '__ARK_TEST.'
    app.database = databases.Database(os.getenv('DATABASE_URL'), force_rollback=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.database.connect())
    yield


@pytest.fixture()
def client(setup):
    return TestClient(app)
