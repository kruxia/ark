# Ark API

API = /api/v1

* / = ok + welcome message
* /auth = OAuth2 authorization endpoints
* /docs = API documentation
* /health = healthcheck on all system components {filestorage, SVN server, PostgreSQL}
* /ark = archive parent 
    * GET = list of archives and their metadata
    * POST = create new archive
* /ark/NAME
    * GET = archive metadata
    * PUT = edit archive + folder metadata
    * POST = create file / folder in this archive
    * DELETE = delete this archive and all its content
* /ark/NAME/files[/PATH]
    * folder 
        * GET = folder metadata and file/folder list
        * PUT = update folder metadata
        * POST = create/update file|folder under this location
        * DELETE = delete this folder and all its content
    * file 
        * GET = file metadata
        * PUT = update file metadata + content
        * DELETE = delete the file
* /ark/NAME/rev = list of revisions with basic metadata
* /ark/NAME/rev/N = metadata about this particular revision
    * GET = get the revision metadata
    * POST = change the revision metadata
