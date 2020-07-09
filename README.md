# Ark

Ark is a file storage server that provides:

* versioning with unlimited file history and optional changelog messaging
* branch–modify–merge (textual) and lock–modify–unlock (binary) collaboration workflows
* event triggers to drive workflow automations and webhooks
* [REST API](api/README.md)
* file interface UI
* full-text-search on file contents and metadata, supporting NN languages
* efficient binary file revision storage [via using Subversion]

Better than Dropbox:

* Check-out+Lock, Modify, Check-in+Unlock workflow help prevent file and workflow conflicts
* unlimited version history — no time limit. 
  [Dropbox limits 30, 180, 365 days. OneDrive, Box store a fixed number of versions.]
* shared content via folder includes [svn:external, like symlink]
  [Other file storage platforms don't have this capability]
* file and folder locking for lock-based collaboration
* revision messages and metadata
* self-hostable, portable, open-source — no vendor lock-in

Architecture:

* File storage server: Apache Subversion
* REST API and search engine: Rust Actix PostgreSQL 
* File interface UI: 
  * XHTML 
  * CSS + {Pure|Tailwind|Boostrap?} 
  * JS + {mithril.js.org|VueJS|React?}
