import os
import asyncio
import http.client
import httpx
from dataclasses import asdict
from api.models import Status, HealthStatus
from api.responses import ORJSONResponse
from starlette.endpoints import HTTPEndpoint


class Health(HTTPEndpoint):
    async def get(self, request):
        files_status, archive_status, database_status = await asyncio.gather(
            archive_files_health(),
            archive_server_health(),
            database_health(request.app.database),
        )
        return ORJSONResponse(
            asdict(
                HealthStatus(
                    files=files_status, archive=archive_status, database=database_status
                )
            )
        )


async def archive_files_health():
    archive_files = os.getenv('ARCHIVE_FILES')
    if os.path.isdir(archive_files):
        return Status(code=200, message="OK")
    else:
        return Status(code=502, message=f"ARCHIVE_FILES not found: {archive_files}")


async def archive_server_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(os.getenv('ARCHIVE_SERVER'))
        code = response.status_code
        message = http.client.responses[code]
    return Status(code=code, message=message)


async def database_health(database):
    try:
        await database.fetch_all("SELECT true")
        code = 200
        message = http.client.responses[code]
    except Exception as err:
        code = 502
        message = f"{http.client.responses[code]}: {err}"
    return Status(code=code, message=message)
