import json
import logging
import os
import http.client
import httpx
import traceback
from lxml import etree
from time import time
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
        s = time()
        records = await request.app.db.fetch_all(
            """
            select * from ark.projects
            """
        )
        logger.debug(f'records time = {time()-s} sec')
        s = time()
        result = await svn.list_archives()
        logger.debug(f'svn time = {time()-s} sec')
        logger.debug(f"{result['data']=}")
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
        except Exception as exc:
            status = Status(code=400, message=f'invalid input: {str(exc)}')
            return JSONResponse(status, status_code=status.code)

        # Creating the archive requires two steps.
        # ------------------------------------------------------------------------------
        # NOTE: It would be better to have both steps in a single transaction, so as to
        # ensure that the database record and the archive are both created or neither.
        # How would we implement that in the context of svn?
        # ------------------------------------------------------------------------------
        try:
            # 1. Create the archive
            result = await svn.create_archive(archive_name)

            # 2. Record the archive in the database
            if result['status'] == 201:
                info = await svn.info(os.getenv('ARCHIVE_SERVER') + '/' + archive_name)
                item = info['data'][0]
                await request.app.db.execute(
                    """
                    INSERT INTO ark.projects 
                    (name, rev, size, created) VALUES 
                    (:name, :rev, :size, :created) RETURNING *
                    """,
                    {
                        'name': archive_name,
                        'rev': item['version']['rev'],
                        'size': item['path']['size'],
                        'created': item['version']['date'],
                    },
                )
            status = Status(
                code=result['status'], message=result['output'] or result['error'] or ''
            )

        except Exception as exc:
            if os.getenv('DEBUG'):
                status = Status(code=500, message=traceback.format_exc())
            else:
                status = Status(code=500, message=str(exc))

        return JSONResponse(status, status_code=status.code)
