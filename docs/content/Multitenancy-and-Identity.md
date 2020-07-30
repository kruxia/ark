2020-07-26

# Account Multitenancy and Identity 

## Multitenancy

Ark must be able to support many accounts, each with its own:

* user(s)
* archive namespace
* search index

The simplest way to achieve this is to have a dedicated set of services for each account — its own

* svn archive service
* api service
* database service
* svndata storage volume
* database index volume
* subdomain

These can all live on a single node for the vast majority of users. For users that need more resources, they can be provided — larger nodes (for database, archive service), more nodes (for api service).

Each account "cluster" (in scare quotes because it is not in fact a cluster, only the concept of a group of services) can further be run using serverless compute like Fargate or AWS Container Instances, and they can be run without dedicated server resources if need be. That way, the instances can be running only when the users are logged into them and using them. (It can also be an option to have "always on" instances, but those will of necessity be more expensive to operate.)

## Identity

One thing that must be shared is the identity provider. There must be a single shared identity service for all Ark accounts that might share a set of users, such as under a single domain. (So it's possible that a large corporate entity will have a self-hosted Ark instance on its own domain, and it also hosts its own identity provider for all of those accounts, integrated with their own SSO.) Sharing an identity provider enables users of an Ark site to have membership in more than one Ark account. 

The shared identity provider lives on a special subdomain, `id.arkhost.tld`, for a given Ark host/top-level domain. All account subdomains interact via OAuth with the `id.` service to obtain an access token with their verified system identity. 

The `id.` service, in turn, can log users in via a variety of mechanisms, including:

* OAuth providers like Google, Twitter.
* Sign in with Apple.
* Azure Active Directory.
* Direct signup + username + password. 

It's feasible in the future that, just as developers use Github.com to sign into other services, users of Ark will end up using it as a primary identity provider. Nevertheless, it's much more likely that they will use their Microsoft, Apple, Google, or Twitter identity first.

The benefits of using one of those signup / login methods are several: No need to remember yet another password, account is secured by industry-leading account security infrastructure at all of those providers, and no need to go through an email / identity verification process after signup.