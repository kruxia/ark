import databases
import os
from starlette.applications import Starlette
from starlette.routing import Route
from api.endpoints.index import Index
from api.endpoints.health import Health


async def app_startup():
    app.database = databases.Database(os.getenv('DATABASE_URL'), min_size=5, max_size=5)
    await app.database.connect()


async def app_shutdown():
    await app.database.disconnect()


routes = [
    Route('/', endpoint=Index),
    Route('/health', endpoint=Health),
]


app = Starlette(routes=routes, on_startup=[app_startup], on_shutdown=[app_shutdown])
