[Ark v1-SLC](_index.md)

# Projects

As a content owner, I want to be able to manage my content in projects, so that I can

* organize content by project
* define project metadata
* assign project-level roles
* define project-level workflows
* track versions by project
* define project environment(s)
* Implementation Notes:

Projects are <1-1> Archives.

We could take a file-centric approach and have all things like project metadata defined in (a) file(s). This would make it easier for those working offline and committing changes to the repository. It would require triggers to update the database whenever changes are committed, and editing in a web interface would function by the same mechanism.

— Yes, that is the best design for serious work. One of the primary problems with past content management systems was that you had to use their interfaces in order to work with your stuff. But if everything is stored in files in the archive, then you can use ANY interface to work with your stuff.

(In fact, this design decision comes into play in the context of writing this story. I want to be able to have all my Epics and Stories defined in Clubhouse, where I'm managing this project and writing these notes. But I also want everything I write and do on this project to be gathered together into a single file system, where I can manage the files and do things like build project documentation. Why can't it be both? Using Ark as a project management system, it _will_ be both: I will be able to write this Epic as a file in the project, and it will also be available in the project management interface. Or vice-versa.)