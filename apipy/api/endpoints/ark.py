import os
import http.client
import httpx
import subprocess
from lxml import etree
from starlette.endpoints import HTTPEndpoint
from api.models import RepositoryInfo
from api.process import run_command
from api.responses import ORJSONResponse


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


class ArkRepo(HTTPEndpoint):
    """
    /ark/NAME = the root for repository NAME
    """

    async def get(self, request):
        """
        Return the metadata for the given repository NAME if it exists, or 404.
        Return 404 NOT FOUND if it doesn't exist.
        """
        archive_server = os.getenv('ARCHIVE_SERVER')
        name = request.path_params['name']
        cmd = ['svn', 'info', '--xml'] + [f"{archive_server}/{name}"]
        result = await run_command(*cmd)
        if bool(result['error']) is True:
            return ORJSONResponse({'code': 404, 'message': 'NOT FOUND'}, status_code=404)
        else:
            xml = etree.fromstring(result['output'])
            entry = xml.xpath('/info/entry')[0]
            info = RepositoryInfo.from_entry(entry).dict()
            return ORJSONResponse(info, status_code=200)

    async def delete(self, request):
        """
        Delete the given repository if it exists, or 404.
        """
        name = request.path_params['name']
        path = f"{os.getenv('ARCHIVE_FILES')}/{name}"
        if not os.path.exists(path):
            response = ORJSONResponse({'code': 404, 'message': 'NOT FOUND'}, status_code=404)
        else:
            cmd = ['rm', '-rf', path]
            subprocess.check_output(cmd)
            response = ORJSONResponse({'code': 200, 'message': f"Deleted '{name}'"}, status_code=200)

        return response