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
    * [x] GET = list of archives and their info
    * [x] POST = create new archive — takes a name parameter in a JSON body
    * [x] pytests
* [ ] /ark/NAME = single archive
  * [ ] python
    * [x] GET = archive info (nothing different from /ark entry)
      <!-- * [ ] POST = edit archive metadata -->
    * [x] DELETE = delete this archive and all its content [The most dangerous endpoint
      in the app, because there is no backup. Until we implement cloud storage backups.]
    * [ ] pytests
* [ ] /ark/NAME/files[/PATH]
  * [ ] python
    * [x] GET = file/folder info, props and list (if folder)
    * [ ] POST = edit this file/folder props
    * [ ] PUT = create/update this file/folder content
    * [ ] DELETE = delete the file/folder and all its content
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
* [ ] /svn[/*] = proxy all requests for the subversion server itself [NOTE: This is a
  good candidate for Rust because it has to be fast and streaming. We have to do
  authentication and authorization before completing the request, which is why it has to
  be proxied.]
* [ ] /auth = OAuth2 authorization endpoints
* [ ] /docs = API documentation (e.g., Swagger)
* [ ] pytests
