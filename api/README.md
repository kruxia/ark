# Ark API

API = /api/v1

* [x] / = 200 OK + welcome message
* [ ] /health = healthcheck on all system components 
    * [x] filestorage — ARCHIVE_FILES
    * [ ] SVN server – ARCHIVE_SERVER
    * [ ] PostgreSQL database – POSTGRES_DSN
    * [x] all at the same time (`futures::join!`)
* [ ] /ark = archive parent 
    * [ ] GET = list of archives and their metadata
    * [ ] POST = create new archive
* [ ] /ark/NAME = single archive
    * [ ] GET = archive metadata
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
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
