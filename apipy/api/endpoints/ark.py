import os
import http.client
import httpx
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.process import run_command
from api.responses import ORJSONResponse


class ArkParent(HTTPEndpoint):
    async def get(self, request):
        """
        list archives and their basic metadata.
        """
        archive_server = os.getenv('ARCHIVE_SERVER')

        # rely on SVNListParentPath to get a list of repositories from the Parent
        async with httpx.AsyncClient() as client:
            response = await client.get(archive_server)
        if response.status_code != 200:
            return ORJSONResponse(
                {
                    'code': response.status_code,
                    'message': http.client.responses[response.status_code],
                }
            )

        # get the list of repository URLs from the response.content
        content = response.content.replace(b'<hr noshade>', b'<hr/>')  # silly HTML
        xml = etree.fromstring(content)
        repository_urls = [
            f"{archive_server}/{name.rstrip('/')}" for name in xml.xpath("//li//text()")
        ]

        # get the svn info for all listed repositories
        cmd = ['svn', 'info', '--xml'] + repository_urls
        result = await run_command(*cmd)
        xml = etree.fromstring(result['output'])
        data = [
            {
                'name': entry.get('path'),
                'uuid': entry.xpath('repository/uuid/text()')[0],
                'rev': int(entry.xpath('commit/@revision')[0]),
                'date': entry.xpath('commit/date/text()')[0],
            }
            for entry in xml.xpath("/info/entry")
        ]
        return ORJSONResponse(data)

    async def post(self, request):
        """
        create a new archive with the given {"name": "..."}
        """
        data = await request.json()
        path = os.getenv('ARCHIVE_FILES') + '/' + data['name']
        cmd = ['svnadmin', 'create', path]
        result = await run_command(*cmd)
        if b'is an existing repository' in result['error']:
            return ORJSONResponse(
                {'code': 409, 'message': f"{data['name']} is an existing repository"}
            )
        else:
            return ORJSONResponse({'code': 201, 'message': f'Created: {data["name"]}'})
