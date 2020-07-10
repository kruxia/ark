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
  * [x] GET / = 
    * [x] 200 OK + welcome message
    * [x] pytest
  * [x] GET /health = 
    * [x] healthcheck on all system components
    * [x] filestorage — ARCHIVE_FILES
    * [x] SVN server – ARCHIVE_SERVER
    * [x] PostgreSQL database – DATABASE_URL
    * [x] all at the same time (`futures::join!`)
    * [x] pytest
  * [x] GET /ark = archive parent
    * [x] list of archives and their info
    * [x] pytest
  * [x] POST /ark = 
    * [x] create new archive — takes JSON body `{"name": "..."}`
    * [x] pytest
  * [ ] GET `/ark/NAME[/PATH]` = single archive or path in the archive
    - [x] info on the path (at HEAD)
    - [x] properties on the path (at HEAD)
    - [x] folder: list of files (at HEAD)
    - [ ] pytest
  * [ ] GET `/ark/NAME[/PATH]?rev=M` = single revision on this archive/path
    - [x] info on the path at the given revision
    - [x] properties on the path at the given revision
    - [x] revision properties for the given revision
    - [x] log on the path at the given revision
    - [x] folder: list of files at the given revision
    - [ ] pytest
  * [ ] GET `/ark/NAME[/PATH]?rev=M:N` = range of revisions on this archive/path
    - [x] log on the path at the given revisions
    - [ ] pytest
  * [ ] POST `/ark/NAME[/PATH]` w/o "rev" in body = 
    - [x] edit this file/folder properties (versioned properties only allowed)
    - [x] 400 if revprops in body
    - [x] delete props listed in `{"propdel": [...]}`
    - [x] 400 if "revpropdel" in body
    - [ ] pytest
  * [ ] POST `/ark/NAME[/PATH]` `{"rev": "M"}`
    - [x] single revision (multiple revisions not allowed)
    - [x] edit the revision properties (editing versioned properties not allowed)
    - [x] 400 if multiple revisions
    - [x] 400 if versioned properties ("props") in body
    - [x] delete revprops listed in `{"revpropdel": [...]}`
    - [x] 400 if "propdel" in body
    - [ ] pytest
  * [ ] PUT `/ark/NAME[/PATH]` = 
    - [x] PATH must be non-empty — cannot PUT to repository root (instead, POST to /ark)
    - [x] create/update this folder/file content 
    - [x] new w/empty body => svn mkdir, non-empty body => svnmucc put
    - [x] mkdir: make directories down to the given path
    - [x] update existing folder w/body makes it a file (replacing it and all children)
    - [x] update w/o body raises conflict
    - [ ] pytest
  * [ ] DELETE `/ark/NAME[/PATH]` = 
    - [x] delete the file/folder/repo and all its content, return 200 with result
    - [x] 404 if not found
    - [ ] pytest
* [ ] /svn[/*] = proxy all requests for the subversion server itself 
  - accept and proxy all svn HTTP methods
  - [NOTE: This is a good candidate for Rust because it has to be fast and streaming. We
    have to do authentication and authorization before completing the request, which is
    why it has to be proxied.]
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
* [ ] pytest
