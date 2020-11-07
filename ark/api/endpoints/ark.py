import json
import logging
import os
import http.client
import httpx
import traceback
from lxml import etree
from time import time
from starlette.endpoints import HTTPEndpoint
from api.types import Result
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
        logger.debug(f'time = {time()-s} sec')
        return JSONResponse(result)

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
            result = Result(status=400, message=f'invalid input: {str(exc)}')
            return JSONResponse(result, status_code=result.status)

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
                archive_name = result['output']
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
            result = Result(
                status=result['status'], 
                message=result.get('output') or result.get('error') or ''
            )

        except Exception as exc:
            if os.getenv('DEBUG'):
                result = Result(status=500, message=traceback.format_exc())
            else:
                result = Result(status=500, message=str(exc))

        return JSONResponse(result, status_code=result.status)
