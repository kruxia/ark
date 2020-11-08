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
        logger.debug(f'time = {time()-s} sec')
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

        try:
            result = await svn.create_archive(archive_name)
        except Exception as exc:
            if os.getenv('DEBUG'):
                result = Result(status=500, message=traceback.format_exc())
            else:
                result = Result(status=500, message=str(exc))

        return JSONResponse(result, status_code=result.status)
