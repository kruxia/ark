import logging
import os
import http.client
import httpx
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.models import Status
from api.responses import JSONResponse
from api import svn

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
        Create a new archive with the given {"name": "..."}.

        201 CREATED = created the archive
        409 CONFLICT = the archive already exists
        """
        try:
            data = await request.json()
            archive_name = data['name']
        except Exception:
            status = Status(code=400, message='invalid input')
            return JSONResponse(status, status_code=status.code)

        result = await svn.create_archive(archive_name)

        if 'is an existing repository' in result['error']:
            status = Status(code=409, message=f"'{archive_name}' already exists")
        elif result['error']:
            status = Status(code=409, message=result['error'])
        else:
            status = Status(code=201, message=f"Created: '{data['name']}'")

        return JSONResponse(status, status_code=status.code)
