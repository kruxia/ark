# Ark API

## 0.1.0

* /api/v1/
  * [x] GET / = 
    * [x] 200 OK + welcome message
  * [x] GET /health = 
    * [x] healthcheck on all system components
    * [x] filestorage — ARCHIVE_FILES
    * [x] SVN server – ARCHIVE_SERVER
    * [x] ~~PostgreSQL database – DATABASE_URL~~ _disabled until we have a db_
  * [x] GET /ark = archive parent
    * [x] list of archives and their info
  * [x] POST /ark = 
    * [x] create new archive — takes JSON body `{"name": "..."}`
  * [x] GET `/ark/NAME[/PATH]` = single archive or path in the archive
    - [x] info on the path (at HEAD)
    - [x] properties on the path (at HEAD)
    - [x] folder: list of files (at HEAD)
  * [x] GET `/ark/NAME[/PATH]?rev=M` = single revision on this archive/path
    - [x] info on the path at the given revision
    - [x] properties on the path at the given revision
    - [x] revision properties for the given revision
    - [x] log on the path at the given revision
    - [x] folder: list of files at the given revision
  * [x] GET `/ark/NAME[/PATH]?rev=M:N` = range of revisions on this archive/path
    - [x] log on the path at the given revisions
  * [x] POST `/ark/NAME[/PATH]` w/o "rev" in body = 
    - [x] edit this file/folder properties
    - [x] delete props listed in `{"propdel": [...]}`
    - [x] 400 if revprops in body w/o props
    - [x] 400 if "revpropdel" in body
  * [x] POST `/ark/NAME[/PATH]` `{"rev": "M"}`
    - [x] single revision (multiple revisions not allowed)
    - [x] edit the revision properties (editing versioned properties not allowed)
    - [x] delete revprops listed in `{"revpropdel": [...]}`
    - [x] 400 if multiple revisions
    - [x] 400 if versioned properties ("props") in body
    - [x] 400 if "propdel" in body
  * [x] PUT `/ark/NAME[/PATH]` = 
    - [x] PATH must be non-empty — cannot PUT to repository root (instead, POST to /ark)
    - [x] create folder / create or update file at this path
    - [x] new w/empty body => svn mkdir, non-empty body => svnmucc put
    - [x] mkdir: make directories down to the given path
    - [x] update existing folder w/body makes it a file (replacing it and all children)
    - [x] update w/o body raises conflict
  * [x] DELETE `/ark/NAME[/PATH]` = 
    - [x] delete the file/folder/repo and all its content, return 200 with result
    - [x] 404 if not found

* [x] /svn[/*] = proxy all requests for the subversion server itself
  - accept and proxy all svn HTTP methods

## TODO: Alpha (_more features_)

* [ ] /auth = OAuth2 authorization endpoints
  - See: <https://docs.authlib.org/en/latest/client/starlette.html> and
    <https://gitlab.com/jorgecarleitao/starlette-oauth2-api>
* [ ] /docs = API documentation (e.g., Swagger)
  - See: <https://github.com/Woile/starlette-apispec> and
    <https://gitlab.com/jorgecarleitao/starlette-oauth2-api>
* [ ] search
* [ ] workflow automation
  
## TODO: Beta 

Do the following before creating a beta release.

* Pin req/install.txt in requirements.txt and use in deploy.Dockerfile
