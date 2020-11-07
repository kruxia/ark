import asyncio
import os
from starlette.endpoints import HTTPEndpoint
from api.responses import JSONResponse
from api.types import NodeKind, Result
from api import svn


class ArkPath(HTTPEndpoint):
    """
    Handle requests to /ark/NAME/PATH, where NAME is an archive name and PATH is a
    file path within the archive. If PATH is empty, then it is "/"
    """

    @classmethod
    def archive_url(cls, request):
        """
        For a given ArkPath request, build and return the archive URL for the request.
        """
        return '/'.join(
            [
                os.getenv('ARCHIVE_SERVER'),
                request.path_params['name'],
                request.path_params.get('path', ''),
            ]
        )

    async def get(self, request):
        """
        GET info and props for the path, list of files and folders if it's a directory
        """
        url = self.archive_url(request)
        request_path = request.path_params.get('path', '')

        kw = {}
        if 'rev' in request.query_params:
            kw['rev'] = request.query_params['rev']

        result = {}

        info, props = await asyncio.gather(svn.info(url, **kw), svn.props(url, **kw))

        if 'data' in info and len(info['data']) > 0:
            result['info'] = info['data'][0]
        if 'data' in props:
            result['props'] = props['data']

        if 'rev' in kw and 'No such revision' not in info['error']:
            revprops, log = await asyncio.gather(
                svn.revprops(url, **kw), svn.log(url, **kw)
            )
            if 'data' in revprops:
                result['revprops'] = revprops['data']
            result['log'] = log['data'] if 'data' in log else []
            # filter the log messages to those that are under this path, relative to this path
            for entry in result['log']:
                if entry.get('paths'):
                    entry['paths'] = list(
                        filter(
                            lambda path: path['name'].startswith(request_path),
                            entry['paths'],
                        )
                    )
                    for path in entry['paths']:
                        if path['name'] == request_path:
                            path['relpath'] = os.path.split(path['name'])[-1]
                        else:
                            path['relpath'] = os.path.relpath(
                                path['name'], os.path.dirname(request_path)
                            )

        if result.get('info', {}).get('path', {}).get('kind') == NodeKind.Dir:
            files = await svn.ls(url, **kw)
            result['files'] = files['data'] if 'data' in files else []

        if result:
            response = JSONResponse(result)
        else:
            result = Result(status=404, message='NOT FOUND')
            response = JSONResponse(result, status_code=404)

        return response

    async def post(self, request):
        """
        Update props for the archive path, return the result
        """
        try:
            data = await request.json()
            assert isinstance(data, dict)
        except Exception:
            result = Result(status=400, message="Invalid JSON body").dict()

        url = self.archive_url(request)
        result = await svn.propset(url, data)
        if result.get('error'):
            result = Result(status=400, message=result['error']).dict()

        return JSONResponse(result, status_code=result.get('code', 200))

    async def put(self, request):
        """
        Create a folder, or create or update a file, at path, if the parent is a
        directory and exists.
        """
        url = self.archive_url(request)
        message = request.query_params.get('message')
        form = await request.form()
        revprops = {
            key: val for key, val in request.query_params.items() if key != 'message'
        }
        file = form.get('file')
        if not file:
            # directory
            result = await svn.put(url, message=message, revprops=revprops)
        else:
            # file
            body = await file.read()
            result = await svn.put(url, body=body, message=message, revprops=revprops)

        return JSONResponse(
            result,
            status_code=result.get('code') or (409 if result.get('error') else 201),
        )

    async def delete(self, request):
        """
        Delete the archive, file, or directory at path
        """
        name = request.path_params['name']
        path = request.path_params.get('path')
        message = request.query_params.get('message')
        url = self.archive_url(request)
        revprops = {
            key: val for key, val in request.query_params.items() if key != 'message'
        }

        if not path:
            # delete archive
            result = await svn.delete_archive(name)
            if result['status'] == 200:
                await request.app.db.execute(
                    """
                    DELETE FROM ark.projects 
                    WHERE name=:name
                    """,
                    {'name': name},
                )
        else:
            # delete file or folder
            result = await svn.remove(url, message=message, revprops=revprops)

        return JSONResponse(result, status_code=404 if result.get('error') else 200)
