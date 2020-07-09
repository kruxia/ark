# Ark API

API = /api/v1

* [x] / = 200 OK + welcome message [2020-07-03]
    * [x] rust
        * [x] GET => StatusMessage
        * [x] test
    * [x] python
        * [x] port
        * [x] pytest
* [x] /health = healthcheck on all system components [2020-07-04]
    * [x] rust
        * [x] filestorage — ARCHIVE_FILES
        * [x] SVN server – ARCHIVE_SERVER
        * [x] PostgreSQL database – DATABASE_URL
        * [x] all at the same time (`futures::join!`)
        * [x] tests
    * [x] python
        * [x] port
        * [x] pytest
* [x] /ark = archive parent
    * [x] python
        * [x] GET = list of archives and their (basic?) metadata
        * [x] POST = create new archive — takes a name parameter in a JSON body
        * [x] pytests
* [ ] /ark/NAME = single archive
    * [ ] python
        * [ ] GET = archive (complete?) metadata
        * [ ] POST = edit archive metadata
        * [ ] DELETE = delete this archive and all its content
        * [ ] pytests
* [ ] /ark/NAME/files[/PATH]
    * [ ] python
        * [ ] folder 
            * [ ] GET = folder metadata and file/folder list
            * [ ] POST = edit folder metadata
            * [ ] DELETE = delete this folder and all its content
            * [ ] pytests
        * [ ] file 
            * [ ] GET = file metadata
            * [ ] POST = edit file metadata
            * [ ] PUT = create/update file content
            * [ ] DELETE = delete the file
            * [ ] pytests
* [ ] /ark/NAME/rev = revisions in this archive
    * [ ] python
        * [ ] GET = list of revisions and basic metadata
        * [ ] pytests
* [ ] /ark/NAME/rev/N = metadata about this particular revision
    * [ ] python
        * [ ] GET = get the revision metadata
        * [ ] POST = edit the revision metadata
        * [ ] pytests
* [ ] /svn[/*] = proxy requests for the subversion server itself
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
* [ ] pytests
