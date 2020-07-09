import os
import http.client
import httpx
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.models import RepositoryInfo
from api.process import run_command
from api.responses import ORJSONResponse


class ArkParent(HTTPEndpoint):
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
                {
                    'code': response.status_code,
                    'message': http.client.responses[response.status_code],
                },
                status_code=response.status_code,
            )

        # get the list of repository URLs from the response.content
        content = response.content.decode().replace('<hr noshade>', '<hr/>').strip()
        xml = etree.fromstring(content)
        repository_urls = [
            f"{archive_server}/{name.rstrip('/')}" for name in xml.xpath("//li//text()")
        ]
        if len(repository_urls) > 0:
            # get the svn info for all listed repositories
            cmd = ['svn', 'info', '--xml'] + repository_urls
            result = await run_command(*cmd)
            xml = etree.fromstring(result['output'])
            data = [
                RepositoryInfo.from_entry(entry).dict()
                for entry in xml.xpath("/info/entry")
            ]
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
                {'code': 400, 'message': 'invalid input'}, status_code=400
            )

        path = os.getenv('ARCHIVE_FILES') + '/' + repo_name
        cmd = ['svnadmin', 'create', path]
        result = await run_command(*cmd)
        if b'is an existing repository' in result['error']:
            return ORJSONResponse(
                {'code': 409, 'message': f"'{repo_name}' is an existing repository"},
                status_code=409,
            )
        else:
            return ORJSONResponse(
                {'code': 201, 'message': f"Created: '{data['name']}'"}, status_code=201
            )
