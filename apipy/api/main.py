import databases
import os
from starlette.applications import Starlette
from starlette.routing import Route
from api.endpoints.index import Index
from api.endpoints.health import Health
from api.endpoints.ark import ArkParent
from api.endpoints.ark_files import ArkFiles


async def app_startup():
    app.database = databases.Database(os.getenv('DATABASE_URL'), min_size=5, max_size=5)
    await app.database.connect()


async def app_shutdown():
    await app.database.disconnect()


routes = [
    Route('/', endpoint=Index),
    Route('/health', endpoint=Health),
    Route('/ark', endpoint=ArkParent),
    Route('/ark/{name}', endpoint=ArkFiles),
    Route('/ark/{name}/{path:path}', endpoint=ArkFiles),
]


app = Starlette(routes=routes, on_startup=[app_startup], on_shutdown=[app_shutdown])