import asyncio
import os
import databases
import pytest
from starlette.testclient import TestClient
from api.main import app


# @pytest.fixture(scope="session")
# def setup():
#     # Rather than going to obscene lengths to create a separate archive server, we just
#     # create test archives with a given prefix to avoid name conflicts.
#     os.environ['ARK_TEST_PREFIX'] = '__ARK_TEST__'

#     # The app isn't running normally, so the database connection (pool) that we usually
#     # create during app startup (api.main.app_startup) has to be done here.
#     app.db = databases.Database(os.getenv('DATABASE_URL'), force_rollback=True)
    
#     # The Database.connect method is async, so it has to be done in the main event loop.
#     # (We use asyncio.get_event_loop() to get the main event loop shared by TestClient.)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(app.db.connect())


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as testclient:
        yield testclient
