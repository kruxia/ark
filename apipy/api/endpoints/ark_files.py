import asyncio
import os
from starlette.endpoints import HTTPEndpoint
from api.responses import ORJSONResponse
from api.models import Status
from api import svn


class ArkFiles(HTTPEndpoint):
    """
    Handle requests to /ark/NAME/files/PATH, where NAME is a repository name and PATH is
    a file path within the repository. If PATH is empty, then it is "/"
    """

    async def get(self, request):
        """
        GET info and props for the path, list of files and folders if it's a directory
        """
        url = '/'.join(
            [
                os.getenv('ARCHIVE_SERVER'),
                request.path_params['name'],
                request.path_params.get('path', ''),
            ]
        ).rstrip('/')

        kw = {}
        result = {}
        if 'rev' in request.query_params:
            kw['rev'] = request.query_params['rev']

        info = await svn.info(url, **kw)
        if 'data' in info:
            props = await svn.proplist(url, **kw)
            result['info'] = next(iter(info['data']), {})
            result['props'] = props['data'] if 'data' in props else {}

        if 'rev' in kw:
            revprops, log = await asyncio.gather(
                svn.revproplist(url, **kw), svn.log(url, **kw)
            )
            if 'data' in revprops:
                result['revprops'] = revprops['data']
            result['log'] = log['data'] if 'data' in log else []

        if result.get('info', {}).get('kind') == 'dir':
            files = await svn.list_files(url, **kw)
            result['files'] = files['data'] if 'data' in files else []

        if result:
            response = ORJSONResponse(result)
        else:
            result = Status(code=404, message='NOT FOUND').dict()
            response = ORJSONResponse(result, status_code=404)

        return response

    async def post(self, request):
        """
        Update props for the path
        """
        return ORJSONResponse(
            Status(code=501, message="NOT IMPLEMENTED").dict(), status_code=501
        )

    async def put(self, request):
        """
        Create or update a file at path, if the parent is a directory and exists.
        """
        return ORJSONResponse(
            Status(code=501, message="NOT IMPLEMENTED").dict(), status_code=501
        )

    async def delete(self, request):
        """
        Delete the file or directory at path
        """
        return ORJSONResponse(
            Status(code=501, message="NOT IMPLEMENTED").dict(), status_code=501
        )
