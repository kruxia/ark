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
        async with httpx.AsyncClient() as client:
            response = await client.get(archive_server)
        if response.status_code != 200:
            return JSONResponse(
                Status(
                    code=response.status_code,
                    message=http.client.responses[response.status_code],
                ),
                status_code=response.status_code,
            )

        # get the list of archive URLs from the response.content
        content = response.content.decode().replace('<hr noshade>', '<hr/>').strip()
        logger.debug(content)
        xml = etree.fromstring(content)
        archive_urls = [
            f"{archive_server}/{name.rstrip('/')}"
            for name in xml.xpath("//li//text()")
            if not name.startswith('.')
        ]
        if len(archive_urls) > 0:
            # get the svn info for all listed repositories
            result = await svn.info(*archive_urls)
            data = result.get('data', [])
        else:
            data = []
        return JSONResponse(data)

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
