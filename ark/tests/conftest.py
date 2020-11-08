import asyncio
import os
import databases
import pytest
from starlette.testclient import TestClient
from api.main import app


@pytest.fixture(scope="session")
def setup():
    # The app isn't running normally, so the database connection (pool) that we usually
    # create during app startup (api.main.app_startup) has to be done here.
    app.db = databases.Database(os.getenv('DATABASE_URL'), force_rollback=True)

    # The Database.connect method is async, so it has to be done in the main event loop.
    # (We use asyncio.get_event_loop() to get the main event loop shared by TestClient.)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.db.connect())

    yield app

    loop.run_until_complete(app.db.disconnect())


@pytest.fixture()
def client(setup):
    return TestClient(app)
