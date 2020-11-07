"""
The svnadmin API provides endpoints that require filesystem access to the archives
themselves -- operations like creating (svnadmin create), deleting (rm -rf), and listing
(ls + du) archives.

The svnadmin API is a WSGI app so that it can run under the same Apache server that
manages the archives themselve, using e.g. mod_wsgi. If mod_asgi were available, we
would use it. If we continue down this path, we might fork mod_wsgi and create it. (BTW,
thank you [Graham Dumpleton](https://github.com/GrahamDumpleton) for writing mod_wsgi.)

Using mod_wsgi pushes us toward using the highest performance WSGI library available.
There is no better than [Falcon Framework](https://falconframework.org/). (Also, the
team behind Falcon are a really great bunch who let me crash their development sprint at
PyCon 2019 and even merged [my PR](https://github.com/falconry/falcon/pull/1522). That
was a lot of fun, and yeah, I have warm feelings.)

(The world loves nginx, and Apache is starting to seem like "so 2000s". But Apache is
the server for subversion, so as long as we're supporting svn, we'll be using Apache.)
"""
import logging
import subprocess
import traceback
import falcon
from svnadmin import svn
from svnadmin.types import Result
import http.client

log = logging.getLogger(__name__)


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
                log.error(traceback.format_exc())
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


class ListArchives:
    def on_get(self, request, response):
        result = svn.list_archives()
        response.media = result.dict()
        response.status = (
            f"{result.status} {http.client.responses.get(result.status) or ''}"
        )


application = falcon.API()
application.add_route('/', Welcome())
application.add_route('/create-archive', CreateArchive())
application.add_route('/delete-archive', DeleteArchive())
application.add_route('/list-archives', ListArchives())
