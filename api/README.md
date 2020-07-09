# Ark API

API = /api/v1

* [x] / = 200 OK + welcome message [2020-07-03]
    * [x] GET => StatusMessage
    * [x] test
    * [x] python
    * [ ] pytest
* [x] /health = healthcheck on all system components [2020-07-04]
    * [x] filestorage — ARCHIVE_FILES
    * [x] SVN server – ARCHIVE_SERVER
    * [x] PostgreSQL database – DATABASE_URL
    * [x] all at the same time (`futures::join!`)
    * [x] tests
    * [x] python
    * [ ] pytest
* [ ] /ark = archive parent 
    * [ ] GET = list of archives and their (basic?) metadata
    * [ ] POST = create new archive — takes a name parameter in a JSON body
* [ ] /ark/NAME = single archive
    * [ ] GET = archive (complete?) metadata
    * [ ] POST = edit archive metadata
    * [ ] DELETE = delete this archive and all its content
* [ ] /ark/NAME/files[/PATH]
    * [ ] folder 
        * [ ] GET = folder metadata and file/folder list
        * [ ] POST = edit folder metadata
        * [ ] DELETE = delete this folder and all its content
    * [ ] file 
        * [ ] GET = file metadata
        * [ ] POST = edit file metadata
        * [ ] PUT = create/update file content
        * [ ] DELETE = delete the file
* [ ] /ark/NAME/rev = revisions in this archive
    * [ ] GET = list of revisions and basic metadata
* [ ] /ark/NAME/rev/N = metadata about this particular revision
    * [ ] GET = get the revision metadata
    * [ ] POST = edit the revision metadata
* [ ] /svn[/*] = proxy requests for the subversion server itself
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
