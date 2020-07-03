# Ark

Ark is a file storage server that provides:

* versioning with unlimited file history and optional changelog messaging
* branch–modify–merge (textual) and lock–modify–unlock (binary) collaboration workflows
* event triggers to drive workflow automations and webhooks
* [REST API](api/README.md)
* file interface UI
* full-text-search on file contents and metadata, supporting NN languages
* efficient binary file revision storage

Better than Dropbox:

* unlimited version history — no time limit
* shared content via folder includes [svn:external, like symlink]
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
