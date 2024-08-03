2024-03-30

## Content

Every content object belongs to an account. Someone owns the content. (It might be useful later to generalize and allow a content item to exist across accounts; that would require a many-to-many relationship between accounts and content, and also a multi-account way of handling the content filepath. (Perhaps filepath is not a foundational attribute of content, but something that can be applied to content in the context of filesystems.).)

Every content object has 1 or more versions of the content item. When the content is edited, a new version is saved. This versioning applies to every attribute of the content, not just the body. There are two ways to handle content versioning: Linear, and Branching with merges. 

Most content versioning systems only provide linear versioning (DVCS systems like git being a notable exception). Linear versioning only allows one person to work on the content at a time, and one line of changes to be pursued. 

A branching strategy allows many lines of changes to be pursued:

- An individual can revise a piece of content in several different directions and then select and merge the ones that contain the desired changes.

- Different individuals can build on previous work without concern about clobbering the previous work -- each version continues to exist. The authors of the previous work can continue to use those versions or can incorporate (merge) changes made in later versions.

- Collaboration, sharing, and remixing are both easier and more flexible.

Content objects eventually have to live in a filesystem. Object storage systems (S3, Storj, Minio, etc.) provide the most efficient and flexible way to store the content itself as files with paths inside of buckets. For the content to be used in a local environment, the content files must have paths that nest into a hierarchy of folders, and each file has a filename for the folder context.

Content IDs: choosing between content addressing, uuid7, location (path).

- content addressing: SHA256 of the content
    - spreads the ids out evenly over the addressable id space
    - very low possibility of hash collision
    - 32 bytes (or 64 hex characters) of storage
    - can be used to verify that the content has not been tampered with

- timestamp-based random ids: UUID7
    - index (temporal data) locality based on timestamp (can be more efficient in database indexing). See <https://www.cybertec-postgresql.com/en/unexpected-downsides-of-uuid-keys-in-postgresql/>
    - low possibility of id collision (extremely low within a single system of record)
    - 16 bytes of storage, database provides native type
    - UUID v7 soon to be available natively in postgresql; see <https://commitfest.postgresql.org/47/4388/>. Meanwhile it is available in application libraries. 

- location-based addressing: account + path
    - many more bytes to store the content.
    - close coupling between the content itself and where it is used.
    - enables path-based access control to happen more expediently.
    - direct mapping between cloud/server/filesystem storage contexts.

Files and Content Items are separate but related

- Every File is/has a Content Item (or a Folder). 
    
    (If we don't use folders internally but just store the path on every file, then we don't need to talk about folders. In that case, look-up is easier but moving files and folders is harder. I spent a lot of time 10~15 years ago automating the generation of paths from filename + parent_id, and in doing recursive CTE searches for that information. I'm not sure it's worth the trouble to do that just to make moving files easier.)

- A File can also have a version history, which is the array (or DAG?) of Content Items that have had that path. Those content items might or might not have a versioning relationship. The "current" content at a given file path is just the last content item to be stored with that path.

- A content item can have many filepaths, as it can be used in many places. For example, a project is typically stored in a folder, with the content stored in a subfolder with a filename; the same content item can be used in many projects.

- A file has a particular content item at a particular version. Updating the file means pointing to a different content item version.

- Files can also be versioned. Like content, they don't necessarily have a linear version history -- checking out a particular version of the files means checking out the latest version of all files in that version's history. [reminds me a little of dealing with database migrations in sqly]

- A Content Version has one base and one optional merge base. (If version 4 was based on version 2 and version 2 was based on version 1, and version 3 was based on version 1, and version 5 merges version 4 and version 3, we could say that version 5 has version 4 as base and version 3 as merge base).
    ```
    1 <----- 3 <-----\
     \<-- 2 <-- 4 <-- 5
    ```

- File versions are grouped together into change sets. These versions (change sets) also have one base and one optional merge base.

- Do we need two separate, parallel versioning systems? 
    
    - Content can exist without being a file in a filesystem. Content does not need to have a filename or folder location applied to it. It gives us greater freedom to be able to operate on content without worrying about the filesystem layer.
    
    - Content can't be represented in a filesystem without a filename and a path. Most of the time (but not all of the time), we want to be able to represent content in a filesystem.

    - The versioning of the files in the filesystem, and the versioning of the content itself, are separate matters, but they are usually closely bound together. Content can be revised without creating a new file version, but usually (but not always) if we revise the content we also want the file in the filesystem (that represents our working tree) to be updated.

    - If we only version files, then we still maintain an implicit version history for content: The new version of a file is a new version for its content. 

    - If the same content is used for two different files, and a new version of one of those files is created, then it is a new version of the content, but only in the context of that file. 
    
It is a reasonable simplification only to version files unless and until the need to version content separately becomes evident.

- Each file is versioned with a change set of versions. A version has many files. A file has many versions. A file version belongs to a single version and file.

- Each file version points has a particular content item created at a particular time.