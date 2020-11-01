import json
import logging
import os
import http.client
import httpx
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.models import Status
from api.responses import JSONResponse
from api import svn
from db import models

logger = logging.getLogger(__name__)


class ArkParent(HTTPEndpoint):
    """
    Endpoint for /ark, the parent location for all repositories
    """

    async def get(self, request):
        """
        List archives and their basic metadata.

        200 OK = List retrieved successfully
        [other status] = the archive server took it badly
        """
        archive_server = os.getenv('ARCHIVE_SERVER')

        # get a list of repositories via SVNListParentPath
        result = await svn.list_archives()
        if result['status'] == 200:
            return JSONResponse(result['data'])
        else:
            return JSONResponse(
                Status(
                    code=result['status'],
                    message=http.client.responses[result['status']],
                )
            )

    async def post(self, request):
        """
        Create a new project with the given {"name": "..."}.

        201 CREATED = created the archive
        409 CONFLICT = the archive already exists
        """
        try:
            data = await request.json()
            archive_name = data['name']
        except Exception:
            status = Status(code=400, message='invalid input')
            return JSONResponse(status, status_code=status.code)

        async with httpx.AsyncClient() as client:
            url = os.getenv('ARCHIVE_SERVER').rstrip('/') + 'admin/create-archive'
            response = await client.post(
                url,
                data=json.dumps({'name': archive_name}),
                headers={'Content-Type': 'application/json'},
            )
            result = response.json()
            status = Status(
                code=response.status_code,
                message=result['output'] or result['error'] or '',
            )

        if response.status_code == 201:
            info = await svn.info(os.getenv('ARCHIVE_SERVER') + '/' + archive_name)
            item = info['data'][0]
            record = await request.app.db.fetch_one("""
                INSERT INTO ark.projects 
                (name, rev, size, created) VALUES 
                (:name, :rev, :size, :created) RETURNING *
                """, 
                {
                    'name': archive_name, 
                    'rev': item['version']['rev'],
                    'size': item['path']['size'],
                    'created': item['version']['date']
                }
            )
            project = models.Project(**record)
            logger.info(f"{project.dict()=}")

        return JSONResponse(status, status_code=status.code)
