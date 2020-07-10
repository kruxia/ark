import logging
import os
import http.client
import httpx
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.models import Status
from api.process import run_command, as_user
from api.responses import ORJSONResponse
from api import svn

logger = logging.getLogger(__name__)


class ArkParent(HTTPEndpoint):
    """
    /ark = the parent location for all repositories
    """

    async def get(self, request):
        """
        list archives and their basic metadata.
        """
        archive_server = os.getenv('ARCHIVE_SERVER')

        # get a list of repositories via SVNListParentPath
        async with httpx.AsyncClient() as client:
            response = await client.get(archive_server)
        if response.status_code != 200:
            return ORJSONResponse(
                Status(
                    code=response.status_code,
                    message=http.client.responses[response.status_code],
                ).dict(),
                status_code=response.status_code,
            )

        # get the list of repository URLs from the response.content
        content = response.content.decode().replace('<hr noshade>', '<hr/>').strip()
        logger.debug(content)
        xml = etree.fromstring(content)
        repository_urls = [
            f"{archive_server}/{name.rstrip('/')}"
            for name in xml.xpath("//li//text()")
            if not name.startswith('.')
        ]
        if len(repository_urls) > 0:
            # get the svn info for all listed repositories
            result = await svn.info(*repository_urls)
            data = result.get('data', [])
        else:
            data = []
        return ORJSONResponse(data)

    async def post(self, request):
        """
        create a new archive with the given {"name": "..."}
        """
        try:
            data = await request.json()
            repo_name = data['name']
        except Exception:
            return ORJSONResponse(
                Status(code=400, message='invalid input').dict(), status_code=400,
            )

        path = os.getenv('ARCHIVE_FILES') + '/' + repo_name
        cmd = ['svnadmin', 'create', path]
        result = await run_command(*cmd, preexec_fn=as_user(100, 101))  # as apache u/g
        if 'is an existing repository' in result['error']:
            return ORJSONResponse(
                Status(
                    code=409, message=f"'{repo_name}' is an existing repository",
                ).dict(),
                status_code=409,
            )
        else:
            return ORJSONResponse(
                Status(code=201, message=f"Created: '{data['name']}'").dict(),
                status_code=201,
            )
