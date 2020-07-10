# Ark API

API = /api/v1

* [x] rust
  * [x] / = 200 OK + welcome message [2020-07-03]
    * [x] GET => StatusMessage
    * [x] test
  * [x] /health = healthcheck on all system components [2020-07-04]
    * [x] filestorage — ARCHIVE_FILES
    * [x] SVN server – ARCHIVE_SERVER
    * [x] PostgreSQL database – DATABASE_URL
    * [x] all at the same time (`futures::join!`)
    * [x] tests

* [x] python
  * [x] / = 200 OK + welcome message
    * [x] GET => StatusMessage
    * [x] pytest
  * [x] /health = healthcheck on all system components
    * [x] filestorage — ARCHIVE_FILES
    * [x] SVN server – ARCHIVE_SERVER
    * [x] PostgreSQL database – DATABASE_URL
    * [x] all at the same time (`futures::join!`)
    * [x] pytest
  * [x] /ark = archive parent
    * [x] GET = list of archives and their info
    * [x] POST = create new archive — takes JSON body `{"name": "..."}`
    * [x] pytest
  * [ ] /ark/NAME[/PATH] = single archive or path in the archive
    * [x] GET = 
      - [x] info on the path (at HEAD)
      - [x] properties on the path (at HEAD)
      - [x] folder: list of files (at HEAD)
      - [ ] pytest
    * [ ] GET `?rev=N` = single revision on this archive/path
      - [x] info on the path at the given revision
      - [x] properties on the path at the given revision
      - [x] revision properties for the given revision
      - [x] log on the path at the given revision
      - [x] folder: list of files at the given revision
      - [ ] pytest
    * [ ] GET `?rev=N:M` = range of revisions on this archive/path
      - [x] log on the path at the given revisions
      - [ ] pytest
    * [ ] POST = edit this file/folder properties (versioned properties only allowed)
    * [ ] POST `?rev=N` = 
      - [ ] edit the revision properties (editing versioned properties not allowed)
      - [ ] pytest
    * [ ] PUT = create/update this folder/file content (update folder has no effect)
    * [ ] DELETE = delete the file/folder/repo and all its content
    * [ ] pytest
  * [ ] /ark/NAME[/PATH]?rev=N = single revision on this archive/path
  * [ ] /ark/NAME[/PATH]?rev=N:M = range of revisions at this archive/path
* [ ] /svn[/*] = proxy all requests for the subversion server itself [NOTE: This is a
  good candidate for Rust because it has to be fast and streaming. We have to do
  authentication and authorization before completing the request, which is why it has to
  be proxied.]
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
* [ ] pytest
