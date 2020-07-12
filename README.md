# Ark

Ark is a file storage server that provides:

* versioning with unlimited file history and optional changelog messaging
* branch–modify–merge (textual) and lock–modify–unlock (binary) collaboration workflows
* event triggers to drive workflow automations and webhooks
* [REST API](api/README.md)
* file interface UI
* full-text-search on file contents and metadata, supporting NN languages
* efficient binary file revision storage [via Subversion] — large repositories with many
  binary files that have numerous revisions typically require only fractionally more
  storage space than the files themselves.

Better than Dropbox:

* Unlimited version history — no time limit, no limit to the number of revisions.
  [Dropbox limits 30, 180, 365 days. OneDrive, Box store a fixed number of versions.]
* Shared content via folder includes [svn:external, like symlink] — no need to copy
  shared files/ [Other file storage platforms don't have this capability]
* Check-out / Modify / Check-in workflow with file and folder locking for collaboration
  without conflicts. 
* Revision messages — easily review progress and find exactly what you're looking for.
  Find and compare different versions of a file spanning years or decades. [Other file
  storage platforms don't provide revision messaging, so you're left guessing or having
  to inspect and compare files manually to see what happened in a given revision.]
* File and revision properties (metadata) — Attach arbitrary key/value pairs to files
  and folders, and the project archive itself, for your own use cases.
* Self-hostable, portable, open-source — no vendor lock-in. [Other cloud file storage
  systems are completely proprietary.]

Architecture:

* File storage server: Apache Subversion
* REST API and search engine: Python Starlette PostgreSQL 
* File interface UI: 
  * XHTML 
  * CSS + {Pure|Tailwind|Boostrap?} 
  * JS + {mithril.js.org|VueJS|React?}
