import os
import asyncio
import http.client
import httpx
from api.types import Result, HealthStatus
from api.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint


class Health(HTTPEndpoint):
    """
    Endpoint for the /health status check.
    """

    async def get(self, request):
        """
        Gather and return health status about all services in the cluster. These include

        * Archive filesystem
        * Archive server
        * PostgreSQL database
        """
        files_status, archive_status, database_status = await asyncio.gather(
            archive_files_health(),
            archive_server_health(),
            database_health(request.app.db),
        )
        return JSONResponse(
            Result(
                data=HealthStatus(
                    files=files_status, archive=archive_status, database=database_status
                )
            )
        )


async def archive_server_health():
    """
    Check the status of the archive server by requesting the server root. It should
    response 200 OK. Return the HTTP response status code and corresponding message.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(os.getenv('ARCHIVE_SERVER'))
    return Result(
        status=response.status_code, message=http.client.responses[response.status_code]
    )


async def database_health(database):
    """
    Check the status of the database server. It should be reachable and able to execute
    a simple query. Return 200 OK if it is, 502 BAD GATEWAY if it is not.
    """
    try:
        await database.fetch_all("SELECT true")
        code = 200
        message = http.client.responses[code]
    except Exception as err:
        code = 502
        message = f"{http.client.responses[code]}: {err}"
    return Result(status=code, message=message)
