import databases
import os
from starlette.applications import Starlette
from starlette.routing import Route
from api.endpoints.index import Index
from api.endpoints.health import Health
from api.endpoints.ark import ArkParent
from api.endpoints.ark_files import ArkPath


async def app_startup():
    """
    On app startup, open a connection pool to the database server. TODO: move the size
    of the connection pool (min_size, max_size) to environment variables.
    """
    app.database = databases.Database(os.getenv('DATABASE_URL'), min_size=5, max_size=5)
    await app.database.connect()


async def app_shutdown():
    """
    On app shutdown, close the database connection pool.
    """
    await app.database.disconnect()


routes = [
    Route('/', endpoint=Index),
    Route('/health', endpoint=Health),
    Route('/ark', endpoint=ArkParent),
    Route('/ark/{name}', endpoint=ArkPath),
    Route('/ark/{name}/{path:path}', endpoint=ArkPath),
]


app = Starlette(routes=routes, on_startup=[app_startup], on_shutdown=[app_shutdown])
