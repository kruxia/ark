# Ark Queue 

As an Ark user, I want a queue that will run automations on my archives, so that things that don't need human intervention can be automated.

## Requirements

* After every commit, a job is entered into the queue for that archive + revision.
* Every revision in an archive must be processed in commit (revision) order. Jobs for revision N+1 must not be run until jobs for revision N are completed.
* Except that some jobs do not require an exclusive lock on the archive and should not block following jobs.
* A complete history of jobs and their outputs must be maintained.
* Updating the database/index of the archive is one of the things that must be automated. 
* Updating the database/index should not be blocked by long-running jobs from previous revisions.
* Jobs can themselves create revisions, which will trigger additional jobs.
* Job definitions are themselves versioned in the archive -- the jobs that are to be run at a given time are defined in the Job workflow definitions that are current at that revision.
* Jobs can be triggered manually as well, or on a particular schedule.
* Some jobs should be canceled when a later version of the same job is initialized, so as to conserve resources. For example, generating distribution-ready PDFs is a heavy process. If this job is triggered by revision N and then again by revision N+1 while the rev N job is still running, the in-process rev N job should be canceled in favor of the N+1 job. These rules should be able to be defined for each job / workflow.
* Separate archives are independent of each other: There are no defined relationships between archives, and no limitation on concurrency between workflows from different archives.

## Implementation

Subversion apparently does not enforce that post-commit hooks will run in revision order: <https://svn.haxx.se/users/archive-2004-07/0541.shtml>. This means that it cannot be relied upon for sequencing.

-   (NOTE: I find myself engineering around the limitations of the SVN platform. Would it be better to implement a new archive platform that takes all of these considerations into account? Yes, perhaps, but (1) it's more practical to get things done by using SVN, as flawed as it is, and (2) doing so we learn and implement what is needed, so that (3) when the time comes to create a new archive platform, we will have the raw materials ready to go.)

So, we need a post-commit queue per archive that will run jobs in strict revision order, and keep track of what the next revision is (so that if rev 3 is inserted into the queue before rev 2, the queue will not initialize the workflow for rev 3 but will wait for rev 2 and initialize that one first).

In essence, the queue itself should be a DAG of dependencies: When a revision is committed, the queue workflow manager looks at the workflow definitions and adds jobs to the queue based on those definitions, with the dependencies that are defined there. 

So, for example, let's suppose that we have this workflow definition:
```yaml
- name: indexing
  depends:
    - PREV
    # * PREV = this task in the previous revision.
    # * PREV:task-name = the named task in the previous revision
- name: build-PDF
  depends:
    - indexing
  cancels:
    - PREV
```

Then we commit some content changes in rev 2 and then again in rev 3 (with the same definitions in place). The DAG would look like this:
```
// <-- means "depends/waits for"
// <!= means "cancels/supersedes"

rev-1:committed <-- rev-2:committed  // added implicitly with rev-2
rev-2:committed <-- rev-2:indexing   // added implicitly with rev-2
rev-2:indexing  <-- rev-2:build-PDF
rev-2:committed <-- rev-3:committed  // added implicitly with rev-3
rev-3:committed <-- rev-3:indexing   // added implicitly with rev-3
rev-2:indexing  <-- rev-3:indexing
rev-2:build-PDF <!= rev-3:build-PDF
rev-3:indexing  <-- rev-3:build-PDF
```

The only job of the post-commit hook is to notify the queue manager that a particular revision on a particular archive has been committed. 

Even though subversion guarantees that commits are transactions, and that rev 2 precedes rev 3, it does not guarantee that the post-commit hook for rev 2 will run before the post-commit hook for rev 3.

Let's suppose that the rev-3 post-commit hook runs before the rev-2 post-commit hook (because subversion doesn't make any guarantees about the order of the hooks). Let's also suppose that `rev-3:build-PDF` is ready to run before `rev-2:build-PDF` has completed (because indexing is fast, `build-PDF` is slow, and `rev-3` was posted before `rev-2`). So, we envision the following sequence of events:

* manager is notified `rev-3:committed` (post-commit hook)
* manager adds workflow entries for `rev-3` to the queue
* manager is notified `rev-2:committed` (post-commit hook)
* manager adds workflow entries for `rev-2` to the queue
* manager logs `rev-2:committed` completed
* manager logs `rev-3:committed` completed
* manager triggers `rev-2:indexing` worker
* manager is notified `rev-2:indexing` completed
* manager triggers `rev-2:build-PDF` worker
* manager triggers `rev-3:indexing` worker
* manager is notified `rev-3:indexing` completed
* manager cancels `rev-2:build-PDF` worker
* manager triggers `rev-3:build-PDF` worker
* manager is notified `rev-3:build-PDF` completed

So, here's how this structure can be implemented:

* When a revision has been committed for an archive, svn post-commit hook posts REPO, REV, and TXN to the queue. (I'm not sure the TXN identifier is needed or useful.)
  (How best to post? Options:)
  - The post-commit script POSTs a request to the API, which logs the commit's workflow to the queue. (Yes: The Ark application API knows how to build a workflow for a commit. This actually means that the queue itself is application agnostic.)
  - The post-commit script INSERTs a record directly to the queue itself. (No: The post-commit script shouldn't know as much as it would need to know about the internal workings of the Ark application or queue system in order to make a correct insertion.)

* In a loop, the Queue Manager:
  * polls the queue for existing tasks, updates the current workflow DAG.
  * triggers any tasks that can be started.
  * listens for a task to finish, but only waits N seconds (1, usu.).
  * updates the queue with the outcome of the task, if any.
  * notifies Task Managers of any running tasks that should be canceled.
  * ~~moves to the journal/archive any tasks that are no longer in play.~~
    - (** How do we know that a task is "no longer in play"? Isn't it possible that a task will come in that depends on an arbitrary earlier task? Especially taking into consideration the possibility of branching and merging in the archive, such that the "previous revision" for any commit could be any other. As a result, it's possible that we never archive tasks - or that we create business rules covering both common cases and fallbacks to handle the unusual situations -- for example, say we normally archive tasks after a week, but if a task comes in that needs an old revision to understand its priors, we can pull that revision out of the archive, find the old task in the task archive, and determine whether it was completed.)

* It's possible to run multiple Queue Managers: Not only can we have separate Managers for separate Queues in the same system, but we can also have multiple Managers for the same Queue, due to the transactional semantics of the Queue database (PostgreSQL's `SELECT FOR UPDATE SKIP LOCKED`).

* Task Managers are separate processes / threads that manage a queue task: launch it, wait for it, and notify the Queue Manager when it has been completed or has failed. The Task Manager also receives signals from the Queue Manager to indicate that a particular Task should be canceled. 

* Task relationship types (DAG edge classes):
  - `depends`: Task B depends on Task A, will wait for it to complete.
  - `cancels`: Task B supersedes Task A and will cancel it if it's in process.

* Workflows files are stored in the Archive in the `_workflows` folder at the root of the archive. 
  - (This folder name works on every system, does not get escaped with url quoting (`+workflows`, `@workflows`), does not conflict with shell command flags (`-workflows`), is not hidden (`.workflows`) does not list with quotes in the shell (`@workflows`) or conflict with shell syntax (`!workflows`), sorts itself close to top of the directory listing (except bottom in Windows CMD shell but top in Explorer), and is unlikely to be used for other kinds of files.)

* Workflow files are `.yaml` and/or `.json` files that define the workflows for the archive. For now, we're only thinking to support post-commit workflows, but others are possible (other kinds of triggers, cron-type repeating tasks). Workflow files are committed to the repository and are processed by the Workflow Manager when it responds to the post-commit hook. 

* The tasks in the workflow files are queued for the given repository at the given revision. If the name of the task is `index`, the rev is `12`, and the archive is `My-Project`, the task's full key will be `{"archive": "My-Project", "rev': 12, "name": "index"}`.

* The following tasks and dependencies are created implicitly for every commit:
  ```yaml
  # the commit itself needs a task definition, which has the primary
  # purpose of ensuring that each commit waits for the previous commits
  # (but not necessarily)
  - name: COMMIT
    depends:
      # in the queue, PREV is the value of the actual previous revision
      - PREV:COMMIT
  # for every task with name:task-name, the follow is created (along 
  # with the rest of the task definition)
  - name: task-name
    depends:
      - COMMIT
  ```
  The COMMIT task is marked as completed when all of its depends are completed. Additional depends can be defined for the COMMIT task (although I'm not sure why you'd want to).

  Task definitions, in addition to the relationships with other tasks in the workflow, must also include information about what the task consists of, how to run it, any required data, etc.
  ```yaml
  - name: task-name
    # depends - any tasks that this task depends on having completed 
    # before starting
    depends:
      - other-task
    # cancels - tasks that will be canceled if this task is ready 
    # before they complete
    cancels:
      - another-task 
    # image - if given, indicates the docker image to use to run the 
    # command/script. If no image is given, the command/script is 
    # run with the default container, which is pre-loaded with ....
    image: image/tag
    # command - a single command to run (either in the system or in 
    # the given image). The given command must already be available.
    command: ...
    # script - instead of a command, the full script can be written.
    script: |
      some command to run
      some other command to run
    # shell - with a script, we have to indicate what shell to use.
    shell: bash
  ```