Ark = Content Workflow Automation Platform

# Milestone: v1.0.0 SLC

## [Projects](projects.md)

* create Project
* Project <1–1> Archive
* Project-level Metadata / Environment
* list Projects
* view Project - dashboard, Files, Members

## [Files in Project](files.md)

* upload / commit Files to Project
* list / browse / search Files in Project(s)
* view File
* annotate File - Annotations are a non-destructive information overlay

## [Workflow Automation](workflow.md)

* define Workflows for Project
* define Triggers for Workflows
* run Workflows
* view status/progress/results of Workflow Jobs
* Job Outputs are stored as Files

## [Users and Auth](users-auth.md)

* OAuth2 provider and consumer
* sign-in with Google, Twitter, Azure, Apple
* Profile loaded from OAuth2 data
* Roles per Installation
    - Admin - delete/archive any project, manage users, manage installation
    - Member - create project, delete/archive own
* Roles per Project
    - Owner - delete/archive project
    - Manager - invite users, manage users' roles
    - Editor - create files, edit any versions
    - Author - create files, edit my versions
    - Reviewer - view files, annotate