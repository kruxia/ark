[Ark v1-SLC](_index.md)

# Users, Authentication, and Authorization

As a site/installation owner, I want to be able to invite other people to use the site so they can host their projects.

As a content/project owner, I want to be able to invite other people to work with me on my content/projects and know that they are able to do work that fits their role.

* Authentication 
    - sign in with Google, Twitter, Azure, Apple
* Roles per site/installation
    - Admin - delete/archive any account, manage users, manage installation
    - Member - create account, manage self-user
* Roles per Account 
    - Owner - delete/archive account
    - Manager - invite users, manage users' roles
    - Editor - create files, edit any versions
    - Author - create files
    - Reviewer - view files and versions, annotate files and versions
    - Reader - view files and versions
* Roles per File
    - Author - edit my files
* Roles per Version
    - Author - edit my versions

## Implementation

- Authentication: Keycloak with RSA-signed JWTs
- Authorization: Permify
