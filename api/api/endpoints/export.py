import asyncio
import os
import tempfile
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse
from api.responses import JSONResponse
from api.models import NodeKind, Status
from api import svn


class ExportPath(HTTPEndpoint):
    """
    Handle requests to /export/NAME/PATH[?REV=N], where NAME is an archive name and PATH 
    is a file path within the archive. If PATH is empty, then it is "/". if REV is 
    given, export at that revision.
    """

    @classmethod
    def archive_url(cls, request):
        """
        For a given ExportPath request, build and return the archive URL for the request.
        TODO: Merge this with the identical method of ArkPath.
        """
        return '/'.join(
            [
                os.getenv('ARCHIVE_SERVER'),
                request.path_params['name'],
                request.path_params.get('path', ''),
            ]
        ).rstrip('/')

    async def get(self, request):
        """
        Export the requested archive path, at the optional requested rev
        200 — exists, returned. 
        404 — not found at the given rev
        """
        url = self.archive_url(request)
        kw = {}
        if 'rev' in request.query_params:
            kw['rev'] = request.query_params['rev']

        result = await svn.export(url, **kw)
        if result.get('filepath'):
            return FileResponse(
                path=result['filepath'], filename=os.path.split(result['filepath'])[-1],
            )
        else:
            raise HTTPException(404)
