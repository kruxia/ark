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
        )
        result = await svn.info(url)
        print(result)
        if 'data' in result:
            info = result['data'][0]
            result = await svn.proplist(url)
            print(result)
            properties = result['data']
            data = {'info': info, 'properties': properties}
            if info['kind'] == 'dir':
                result = await svn.list_files(url)
                print(result)
                data['files'] = result.get('data', [])
            response = ORJSONResponse(data)
        else:
            response = ORJSONResponse(
                Status(code=404, message='NOT FOUND').dict(), status_code=404
            )

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
