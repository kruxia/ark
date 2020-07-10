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
    * [x] pytests
  * [ ] /ark/NAME[/PATH] = single archive or path in the archive
    * [x] GET = 
      - info on the path (at HEAD)
      - properties on the path (at HEAD)
      - folder: list of files (at HEAD)
    * [ ] POST = edit this file/folder properties (versioned properties only allowed)
    * [ ] PUT = create/update this folder/file content (update folder has no effect)
    * [ ] DELETE = delete the file/folder/repo and all its content
    * [ ] pytests
  * [ ] /ark/NAME[/PATH]?rev=N = single revision at this archive/path
    * [ ] GET =
      - info on the path at the given revision
      - properties on the path at the given revision
      - revision properties for the given revision
      - log on the path at the given revision
      - folder: list of files at the given revision
    * [ ] POST = edit the revision properties (editing versioned properties not allowed)
    * [ ] pytests
  * [ ] /ark/NAME[/PATH]?rev=N:M = range of revisions at this archive/path
    * [ ] GET =
      - revision properties for the given revisions
      - log on the path at the given revision
    * [ ] pytests
* [ ] /svn[/*] = proxy all requests for the subversion server itself [NOTE: This is a
  good candidate for Rust because it has to be fast and streaming. We have to do
  authentication and authorization before completing the request, which is why it has to
  be proxied.]
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
* [ ] pytests
