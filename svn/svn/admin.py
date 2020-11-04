import subprocess
import traceback
import falcon
from svn import svn
from svn.types import Result
import http.client


class Welcome:
    def on_get(self, request, response):
        output = 'Welcome to the Ark SVN Admin'
        response.media = {'output': output, 'status': 200}


class CreateArchive:
    def on_post(self, request, response):
        data = request.media

        if 'name' not in data:
            result = Result(error='A new archive must have a name.', status=400)
        else:
            try:
                result = svn.create_archive(data['name'])
            except Exception as exc:
                result = Result(
                    error=str(exc), traceback=traceback.format_exc(), status=500
                )

        response.media = result.dict(exclude_none=True)
        response.status = (
            f"{result.status} {http.client.responses.get(result.status) or ''}"
        )


class DeleteArchive:
    def on_post(self, request, response):
        data = request.media

        if 'name' not in data:
            result = Result(
                error='The archive to be deleted must be named.', status=400
            )
        else:
            try:
                result = svn.delete_archive(data['name'])
            except Exception as exc:
                result = Result(
                    error=str(exc), traceback=traceback.format_exc(), status=500
                )

        response.media = result.dict(exclude_none=True)
        response.status = (
            f"{result.status} {http.client.responses.get(result.status) or ''}"
        )


application = falcon.API()
application.add_route('/', Welcome())
application.add_route('/create-archive', CreateArchive())
application.add_route('/delete-archive', DeleteArchive())
