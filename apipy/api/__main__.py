import asyncio
import databases
import http.client
import httpx
import os
from dataclasses import asdict
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from .models import StatusMessage, HealthStatus


app = FastAPI()
app.database = databases.Database(os.getenv('DATABASE_URL'), min_size=5, max_size=5)


@app.on_event("startup")
async def startup():
    await app.database.connect()


@app.on_event("shutdown")
async def shutdown():
    await app.database.disconnect()


@app.get('/', response_class=ORJSONResponse)
async def index():
    return asdict(StatusMessage(status=200, message='Welcome to the Ark API'))


@app.get('/health', response_class=ORJSONResponse)
async def health():
    files_status, archive_status, database_status = await asyncio.gather(
        archive_files_health(), archive_server_health(), database_health()
    )
    return asdict(
        HealthStatus(
            files=files_status, archive=archive_status, database=database_status
        )
    )


async def archive_files_health():
    archive_files = os.getenv('ARCHIVE_FILES')
    if os.path.isdir(archive_files):
        return StatusMessage(status=200, message="OK")
    else:
        return StatusMessage(
            status=502, message=f"ARCHIVE_FILES not found: {archive_files}"
        )


async def archive_server_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(os.getenv('ARCHIVE_SERVER'))
        code = response.status_code
        message = http.client.responses.get(code, '')
    return StatusMessage(status=code, message=message)


async def database_health():
    try:
        await app.database.fetch_all("SELECT true")
        code = 200
        message = http.client.responses[code]
    except Exception as err:
        code = 502
        message = f"{http.client.responses[code]}: {err}"
    return StatusMessage(status=code, message=message)
