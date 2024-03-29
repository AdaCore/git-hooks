AdaCore Git Hooks
=================

This directory contains the AdaCore Git Hooks.

The AdaCore Git Hooks project provides a set of scripts to be used as
server-side hooks for git repositories.  In addition to those scripts,
it also provides a testsuite to validate those scripts. Although
initially developed to suit AdaCore's needs, these hooks have been
designed with flexibility in mind, so as to be easily usable outside
of AdaCore.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation; see COPYING3 for a copy of the license.

Python Requirements
-------------------

These hooks require Python 3.8 or more recent.  The Python
interpreter used by the hooks is the first executable called
"python" found on the PATH.

Enabling the Hooks
------------------

The hooks have been designed to work with both bare and non-bare
repositories. But typical usage will be with bare repositories.

To enable the hooks, an administrator needs to replace the `hooks`
directory in your git repository by a link to the `/hooks` directory
from a `git-hooks` checkout, and configure them as outlined below.

Minimum Configuration
---------------------

The following config options must be set for **all** repositories.
Updates of any kind will be rejected with an appropriate error message
until minimum configuration is satisfied.

* `hooks.from-domain`

* `hooks.mailinglist`

See below for a description of these config options.

Configuration File
------------------

### Configure File Location

The hooks configuration is loaded from a file named `project.config`
in branch `refs/meta/config`. This file follows the same format as
the various git "config" files (Eg. $HOME/.gitconfig).

### Configure File Update Procedure

To update your repository's configuration and make it operational,
you will need to do the following:

* Download the existing configuration from Gerrit:

  ```console
  $ git fetch origin refs/meta/config
  $ git checkout FETCH_HEAD
  ```

* You are now in **detached HEAD** mode.

* Update the `project.config` file to add/update the git-hooks configuration.

  This can be done using the git config command. For instance:

  ```console
  $ git config -f project.config --add hooks.from-domain example.com
  $ git config -f project.config --add hooks.mailinglist prj-cvs@example.com
  ```

* Verify the `project.config` file contents, and in particular
  the new `[hooks]` section:

  ```
  [hooks]
      from-domain = example.com
      mailinglist = prj-cvs@example.com
  ```

* Commit the configuration change, and push it back:

  ```console
  $ git commit -a -m "Notify prj-cvs@example.com of changes"
  $ git push origin HEAD:refs/meta/config
  ```

### Limitations When Updating the Configuration File

These hooks do not allow pushes trying to combine multiple reference
updates if `refs/meta/config` is one of those references.
In other words, updates to the configuration file must be pushed
on their own, independently of any other reference updates. Otherwise,
the entire push operation is rejected with an error message.


Note About [list] Options
-------------------------

Some of the configuration options supported by git-hooks are documented
as `lists` (Eg: a list of references). For such options, the value of
that configuration option can be specified with either:

* One entry in the configuration file per element in the list; Eg:

  ```
      no-emails = refs/heads/fsf-.*
      no-emails = refs/heads/thirdparty
  ```

* *(deprecated)* One entry in the configuration file, with each element
  of the list separated by comas;

  :warning: *Note that this method is deprecated, as considered harder
  to read compared to the one-entry-per-line method. You should avoid
  using it, as support for this format might be removed at some point.*

  Example:

  ```
      no-emails = refs/heads/fsf-.*, refs/heads/thirdparty
  ```

*Note also that, for [list] options which are documented to have a non-empty
default value, it is currently not possible to override that default.*


Note About Reference Name Matching
----------------------------------

For any configuration option which provides the ability to use regular
expressions to match references by name, the regular expression must match
the entire reference name.

For instance, consider the following configuration:

```
    no-emails = refs/heads/master
```

The `no-emails` configuration matches the reference
`refs/heads/master`, but **not** `refs/heads/master-two` because
the suffix `-two` in `master-two` is not covered by the regular
expression used in the `no-emails` configuration.

Configuration Options for General Use
-------------------------------------

The following config options are available for general use:

* **`hooks.allow-delete-branch`** [list]:

  A list of regular expressions matching reference names corresponding
  to branches that are allowed to be deleted.

  This option is only relevant when the `hooks.restrict-branch-deletion`
  option is set to `true`. Otherwise, any branch can be deleted.

* **`hooks.allow-delete-tag`** (default value: **false**):

  By default, deleting a tag is not allowed. To allow it, set
  this option to `true`.

* **`hooks.allow-non-fast-forward`** [list]:

  A list of regular expressions matching reference names.

  By default, non-fast-forward updates are only allowed on 'topic'
  branches (ie references whose name start with `refs/heads/topic/`).
  This option allows us to extend the list of references where
  non-fast-forward updates are allowed.

* **`hooks.allow-lightweight-tag`** (default value: **false**):

  Lightweight Tags (as opposed to *Annotated Tags*) are really not meant
  to be shared, and thus the hooks will reject updates that create a new
  lightweight tag, unless this config option is defined to `true`.

* **`hooks.branch-ref-namespace`** [list]:

  A list of regular expressions matching reference names which
  are considered to be branches.  Each entry in this list extends
  the list of references that are recognized as branches by
  this repository.

  Unless the `hooks.use-standard-branch-ref-namespace` option is set to
  `false`, this namespace implicitly includes the necessary information
  to recognize all standard branches, as well as branches used by
  Gerrit.

* **`hooks.combined-style-checking`** (default value: **false**):

  By default, the pre-commit checks are performed on each commit
  individually. This ensures that none of the commits introduce some
  style violations. But some developers have found that this policy
  gets in the way more than it helps, and thus requested that the
  pre-commit checks be performed on the combination of all commits.

  The general recommendation is to keep commit-by-commit style checks.
  But to enable combined style-checking, set this config option to
  `true`.

* **`hooks.commit-email-formatter`**:

  If defined, this is the name of a script used to customize
  the contents of the emails sent when new commits are pushed.

  The script is called during the post-receive phase, once per commit
  for which a commit email is to be sent. The script is called with
  the following two arguments:
  - The name of the reference being updated;
  - The SHA1 of the commit.

  Additionally, some extra information about the commit is passed
  to the script via standard input, as a JSON directory, with
  the following key/value pairs:
    - `"email_default_subject"`: The email subject to be used by default,
      if not overridden by this script.
    - `"email_default_body"`: The email body to be used by default,
      if not overridden by this script.
    - `"email_default_diff"`: The patch to include in the email, unless
      overridden by this script.
    - The same key/value pairs as the ones provided to the
      `hooks.commit-extra-checker` script.

  This script is expected to return via standard output a dictionary
  in JSON format, with the following key/value pairs:
    - `"email_subject"` (optional): A string containing the subject of
      the email to send for that commit.
    - `"email_body"` (optional): A string containing the body of the email
      to send for that commit. Note that handling of the "diff" part of
      the email is handled separately (see `"include_diff"` key below).
    - `"diff"` (optional): A string including the text to be included
      in the "Diff:" Section of the email.

  Omitting any of the keys in the return value indicates that the
  project does not wish to customize the corresponding part of
  the commit email, and the hooks will use the default contents
  for that part of the email.

  For instance, to change the email subject while keeping the same
  email body and diff, the script should return a dictionary with
  one element under the `"email_subject"` key, and all other keys
  should be omitted.

  If the script returns a nonzero status code (indicating a failure),
  or returns data in an invalid format, the default email is sent out,
  augmented with a warning showing the error that occurred while calling
  the script.

* **`hooks.commit-extra-checker`**:

  If defined, this is the name of a script to be called during
  the validation phase of a reference update. The purpose of this script
  is to provide support for customized validation rules.

  The script is called once for each new commit of each reference
  being updated, and takes two parameters:
  - The name of the reference being updated;
  - The SHA1 of the commit.

  Additionally, the following information about the commit is passed
  to the script via standard input as a JSON dictionary, with the following
  information (key/value pairs):
  - `"rev"`: The commit's revision (SHA1);
  - `"ref_name"`: The name of the reference being updated;
  - `"ref_kind"`: The kind of **reference** we are updating; either:
    - `"branch"`: A branch;
    - `"notes"`: A Git Notes branch;
    - `"tag"`: A tag. Note that annotated tags can be distinguished
      from lightweight tags by checking the `"object_type"` (`"tag"`
      for annotated tags, and `"commit"` for lightweight tags).
      :warning: Note also that this `"ref_kind"` can be misleading:
      The commit being given is **not** some kind of tag, as the value
      may suggest, but rather an actual commit (like a commit from
      a branch) which hasn't been pushed yet. We are therefore called
      in a very similar situation to a branch update, asked to validate
      new commits. Projects may elect to reject these on the basis
      that this is unusual, and might indicate the user made an error
      somewhere.
  - `"object_type"`: The commit's object type (see `git cat-file -t`);
  - `"author_name"`: The name of the author of the commit;
  - `"author_email"`: The email address of the author of the commit;
  - `"subject"`: The commit's subject;
  - `"body"`: The commit's raw body (unwrapped subject and body);

  The script should return 0 if the update is accepted, or nonzero
  if the update is rejected.

  The script's output is always redirected to the user (stdout and
  stderr, both). While this can obviously be used to relay error
  messages when an update is rejected, some scripts may find it
  useful in cases where the update is accepted as well.

  :warning: The current working directory (cwd) when this script gets
  called is undefined, so it is recommended to provide a full path to
  that script.

* **`hooks.commit-url`**:

  If defined, a URL to be provided at the start of every commit email
  notification. The following placeholders can be used:

  * `%(ref_name)s`: The name of the reference being changed;
  * `%(rev)s`: The commit's SHA1.

  Python string substitution is applied, so `%` characters must be
  escaped using `%%`.

* **`hooks.disable-email-diff`** (default value: **false**):

  If True, "diffs" are not included in the emails describing each new commit.

* **`hooks.disable-merge-commit-checks`** (default value: **false**):

  If set to True, disable the precommit-check in charge of detecting
  unintentional merge commits (see [Pre-commit Checks on the Revision
  History](#pre-commit-checks-on-the-revision-history) for more
  information on this check).

  :warning: The use of this option is **strongly discouraged**, as
  it helps catch mistakes that are easily done, especially by git users
  who are less experimented.

* **`hooks.email-new-commits-only`** [list]:

  A list of regular expressions matching some reference names for which
  commit emails should only be sent for the commits that are new to
  the entire repository (as opposed to just being new to the branch
  being updated). In other words, if performing an update to a reference
  matching this config option, commits found in another pre-existing
  reference will not trigger a commit email.

* **`hooks.file-commit-cmd`**:

  A command called with each commit triggering a commit notification
  email. The purpose of this config variable is to allow the use of
  an ad hoc script when the filing of commits in bug tracking software
  cannot be done simply by just sending an email.

  This provided command is called as is, with the same contents as
  the commit email minus the "diff" part passed via the script's
  standard input.

* **`hooks.force-precommit-checks`** [list]:

   A list of regular expressions matching some reference names for which
   precommit checks should be applied to all new commits being pushed
   to the reference, even if those commits already existed in another
   reference.

   The exception to this rule is when creating a new branch, in which
   case this option is ignored (for the avoidance of doubt, precommit
   checks will continue to be applied to commits which are new to the
   repository).

   By default, precommit checks are only applied to commits which are
   entirely new to the repository. The rationale is that commits which
   are good for one branch are good for all branches.

   This option allows projects to change that policy for the branches
   of their choice, and have the precommit checks always be performed
   against all new commits pushed to any of those branches, even for
   the commits which already exist in another reference.

* **`hooks.from-domain`**:

  The domain name of the email address used in the 'From:' field for all
  email notifications being sent (the local part of the email address -
  before the '@' -, is simply the user name on the host where the hooks
  are running).

* **`hooks.frozen-ref`** [list]:

  The list of references for which updates are not allowed. This is
  typically used to prevent users from pushing commits to former
  development branches which have since been closed.

  For instance, the following example shows how to disallow changes to the
  gdb-7.4 and gdb-7.5 branches:

  ```
      frozen-ref = refs/heads/gdb-7.4
      frozen-ref = refs/heads/gdb-7.5
  ```

* **`hooks.ignore-refs`** [list]:

  A list of *regular expressions* matching some reference names for which
  updates should should be ignored.

  This is mostly meant for sites that use a review system which adds its
  own layer between the user's repository, and the reference repository
  for which the git-hooks are installed.

  This option includes the following entries by default, which are meant
  to match references created by gerrit for its own internal purposes:

  ```
      ignore-refs = refs/changes/.*
      ignore-refs = refs/users/.*/edit-.*
  ```

* **`hooks.mailinglist`**:

  A list of email addresses where to send all email notifications.

  An entry can also be a script instead of an email address, in which
  case the script will be executed to determine the list of recipients
  for that script. See [Using a Script in
  hooks.mailinglist](#using-a-script-in-hooks.mailinglist) for more
  details on how this works.

* **`hooks.max-commit-emails`** (default value: **100**):

  This is mostly a safe-guard against updates with unintended
  consequences in terms of the number of emails being sent out.
  If an update is pushed such that the update would trigger a number
  of commit email notifications greater than the value of this config
  option, the hooks will reject this update.

  Typically, this happens when a developer merges a large number of
  changes from an external source, and then pushes this merge into
  the repository. The recommended approach to handling these merges
  is to first push the external commits to a branch for which commit
  emails are explicitly disabled (see `hooks.no-email`), after which
  the merge can be pushed. When done this way, only one commit email
  will be sent, for the merge commit.

* **`hooks.max-email-diff-size`** (default value: **100,000**):

  This config option ensures that patches sent out inside commit email
  notifications do not exceed a certain size, clogging the mailbox
  of all recipients. Past a certain size, which is configured via
  this config option, the diff isn't likely to be useful anymore, and thus
  gets truncated. A small note is added at the end of the truncated diff
  to indicate that the truncation took place.

* **`hooks.max-filepath-length`** (default value: 150):

  This config option helps ensuring that repositories do not include
  files whose path length, relative to the root of the repository,
  exceeds this value. This is aimed for users using filesystems
  with tools which might have a very low limit in terms of maximum
  path length (users on Windows, for instance).

  The check is only performed for files being added (new files).
  If a file already exists in the repository, future commits modifying
  such a file will not trigger this check, even if the file's path
  length exists the current maximum.

  Setting this config option to zero turns this check off entirely.

* **`hooks.max-ref-names-in-subject-prefix`** (default value: 2):

  For emails corresponding to operations that affect more than one
  reference, the git-hooks try to list all the references in
  the email's subject prefix. E.g.

     [project-name/branch1,branch2]

  This config option control the maximum number of references being
  listed in that subject prefix. If the number of references exceeds
  this config, only the first max-ref-names-in-subject-prefix are
  listed, followed by and ellipsis indicating that the list of
  references is incomplete.

  One example where the configuration can be useful is for emails
  associated to Git Notes updates. When pushing a note, the annotated
  commit may be contained in several branches/references.

* **`hooks.max-rh-line-length`** (default value: 76):

  The maximum length for each line in the revision log. If any line
  exceeds that length, the commit will be rejected. Setting this
  variable to zero turns this check off entirely.

  *:information_source: We used a default limit of 76 characters
  instead of 80, because git commands have a tendency to indent the
  revision history by 4 characters. Similarly, the git hooks also send
  emails where the revision history also gets indented by 4 characters.
  This limit ensures that all lines of a commit revision history fit in
  a standard 80-characters wide terminal.*

* **`hooks.no-emails`** [list]:

  A list of regular expressions matching some reference names for which
  updates should not trigger any email notification.  More precisely,
  this options behaves as follow:

    - When pushing an update to a reference matching this configuration,
      commit email notifications are turned completely off (an
      information banner is printed to remind the user);

    - When pushing an update to a reference which does not match
      this configuration, **except for commits which are first parents
      of the reference being updated**, commit email notifications
      are turned off for all commits which are already contained
      in other references matching this configuration.

      :warning: As hinted above, for references which do not match
      this configuration, we **always send commit emails for first
      parent commits**. This avoids that changes first pushed to
      "development" branches for which there is a no-emails
      configuration and then later merged via a fast-forward merge
      get silently pushed.

  This configuration includes the following entries by default:

  ```
      # The reference that Gerrit uses for annotating commits which have
      # been reviewed and "submitted" (pushed, in Git parlance).
      #
      # Sending commit emails for those commits is unnecessary, because
      # it would be sent at the same time as the email sent for the commit
      # it annotates, with information that users rarely need to consult.
      no-emails = refs/notes/review
  ```

  The example below turns off email notifications for all branches whose
  name start with "fsf-", as well as the "thirdparty" branch:

  ```
      no-emails = refs/heads/fsf-.*
      no-emails = refs/heads/thirdparty
  ```

  *:information_source: Note that this option takes precedence over
  the `hooks.email-new-commits-only` option.*

* **`hooks.no-precommit-check`** [list]:

  A list of regular expressions matching some reference names for which
  pre-commit checks should not be enabled. :warning: Note that this disables
  all pre-commit checks, including the revision history checks. It is
  therefore recommended that this option be **only used for branches
  mirroring development done outside of the community**.

  This is typically used for branches tracking external repositories.

  The example below turns pre-commit-checks off for all branches whose
  name start with "fsf-", as well as the "thirdparty" branch.

  ```
      no-precommit-check = refs/heads/fsf-.*
      no-precommit-check = refs/heads/thirdparty
  ```

* **`hooks.no-rh-character-range-check`** (default value: **false**):

  When set to `false` (the default), the hooks verify that all the characters
  used in the revision log of new commits are within a certain range,
  more specifically that all characters are within the ISO-8859-15 charset.

  This check was introduced primarily to reject non-printable characters
  in revision logs, with the understanding that it does have the side-effect
  of limiting the characters that can be used to the Latin character set.
  Projects that need to allow characters outside the Latin character set,
  and/or want to allow non-printable characters in revision logs, should
  set this configuration to `true`.

* **`hooks.no-rh-style-checks`** [list]:

  A list of *regular expressions* matching some reference names for which
  style-checking of the revision logs should not be enabled. :warning:
  The use of this option is strongly discouraged for branches maintained
  by AdaCore.

  :information_source: Note that Revision History style-checks can be
  disabled for a specific commit by using the sequence `no-rh-check`
  in the revision history.

  The example below turns revision logs style-checking off for all
  branches whose name start with "fsf-", as well as the "thirdparty"
  branch.

  ```
      no-precommit-check = refs/heads/fsf-.*
      no-precommit-check = refs/heads/thirdparty
  ```

* **`hooks.no-style-checks`** [list]:

  A list of *regular expressions* matching some reference names for which
  style checking of the contents of files modified should not be enabled.

  This can be useful in contexts where the repository is a clone of
  a repository where the coding style might not match the standards
  required by the style checker being used, and is an alternative
  to creating/modifying a {.gitattribute} file to add a `no-precommit-check`
  attribute for all files; this configuration option has the advantage of
  not creating a local change in the repository sources, as it is stored
  in the repository's configuration instead.

* **`hooks.pre-receive-hook`**:

  If defined, this is the name of a script to be called at the end of
  the `pre-receive` hook. The script is called exactly the same way
  git itself calls the pre-receive hook, and therefore should allow
  customized pre-receive processing. The script should return non-zero
  to reject the entire update.

  The script's output is always redirected to the user (both stdout
  and stderr). While this can obviously be used to relay error
  messages when an update is rejected, some scripts may find it
  useful in cases where the update is accepted as well.

  :warning: The current working directory (cwd) when this script gets
  called is undefined, so it is recommended to provide a full path to
  that script.

* **`hooks.post-receive-hook`**:

  If defined, this is the name of a script to be called at the end of
  the `post-receive` hook. The script is called exactly the same way
  the post-receive hooks is called, and therefore should allow customized
  post-receive processing.

  :warning: The current working directory (cwd) when this script gets
  called is undefined, so it is recommended to provide a full path to
  that script.

* **`hooks.reject-merge-commits`** [list]:

  A list of regular expressions matching some reference names for which
  merge commits are not allowed.

  The example below causes merge commits to be rejected on branch
  "master" and all branches whose name start with "gdb-".

  ```
      reject-merge-commits = refs/heads/master
      reject-merge-commits = refs/heads/gdb-.*
  ```

* **`hooks.rejected-branch-deletion-tip`**:

  This option is used when a developer tries to delete a branch, and
  the deletion is rejected (see `hooks.restrict-branch-deletion`).
  When this happens, the hooks print an error message explaining
  why the deletion was rejected, and concludes with a paragraph
  providing some generic suggestions on how to move forward.

  When defined, this option provides some text which is printed
  in lieu of the generic instructions on how to move forward.
  This option therefore allows projects to provide instructions
  which are completely specific to the project, as a way to be
  more helpful to their developers.

  Example:
  ```
  [hooks]
      rejected-branch-deletion-tip = \
      If you are trying to delete a branch which was created\n\
      by accident, then please contact your favorite admin\n\
      and he will take care of removing the branch for you.
  ```

* **`hooks.restrict-branch-deletion`** (default value: **false**):

  When set to `true`, the only branches that can be deleted are
  the branches listed in the repository's `hooks.allow-delete-branch`
  configuration.

  When `false`, branch deletion is not restricted.

* **`hooks.style-checker`** (default value: `style_checker`):

  If provided, the program to call when performing style checks.
  It is expected that this program follow the same calling convention
  as `style_checker` (see https://github.com/adacore/style_checker
  for more details).

  It is recommended that, unless located in a very standard location
  always included in the PATH (Eg: /usr/bin), the full path to the program
  be specified.

* **`hooks.style-checker-config-file`**:

  If provided, the name of a config file, relative to the repository's
  root directory, to be used by the `style_checker` as a repository-specific
  configuration file (passed via the `--config CONFIG_FILENAME`
  command-line option).

* **`hooks.tag-ref-namespace`** [list]:

  Same as `hooks.branch-ref-namespace`, but for tags.

  Unless the `hooks.use-standard-tag-ref-namespace` option is set to
  `false`, this namespace implicitly includes the necessary information
  to recognize all standard tag reference names.

* **`hooks.tn-required`** (default value: **false**):

  *[This is an AdaCore-specific option]*

  If set to `true`, the hooks verify that the revision history of all new
  commits contain a Ticket Number, and reject the update if it is not
  the case.

  This requirement can be by-passed by using the word `no-tn-check` in the
  revision history, in lieu of the Ticket Number.

* **`hooks.update-hook`**:

  If defined, this is the name of a script to be called during
  the validation phase of a reference update. The purpose of this script
  is to provide support for customized validation rules.

  The script is called once for each reference to be updated, and takes
  three parameters:
  - The name of the reference being updated;
  - the old object name stored in the reference;
  - and the new object name to be stored in the reference.

  The script should return 0 if the update is accepted, or nonzero
  if the update is rejected.

  The script's output is always redirected to the user (stdout and
  stderr, both). While this can obviously be used to relay error
  messages when an update is rejected, some scripts may find it
  useful in cases where the update is accepted as well.

  :warning: The current working directory (cwd) when this script gets
  called is undefined, so it is recommended to provide a full path to
  that script.

* **`hooks.use-standard-branch-ref-namespace`** (default value: **true**):

  If `true`, the `hooks.branch-ref-namespace` implicitly includes
  the necessary information to recognize all standard branches,
  as well as branches used by Gerrit. If set to `false`, then
  `hooks.branch-ref-namespace` starts empty.

  This option is useful in the case where repositories want to restrict
  the list of branches allowed in the standard namespace. These repositories
  then start by setting this option to `false`, and then specify
  the exact namespace that they want to allow and enforce via
  the `hooks.branch-ref-namespace` option.

* **`hooks.use-standard-tag-ref-namespace`** (default value: **true**):

  Same as `hooks.use-standard-branch-ref-namespace`, but affecting
  the `hooks.tag-ref-namespace` configuration.

Configuration Options for Debugging
-----------------------------------

The following config options are recognized, but are only meant to
be used for debugging/testing purposes. They should not be used
during normal operations.

* **`hooks.bcc-file-ci`** (default value: **true**):

  :information_source: This is an AdaCore-specific option which,
  in this version of the git-hooks, can only be activated while
  inside the testsuite. AdaCore deploys a slightly modified
  version where this feature is activated by default for all
  repositories.

  Setting this config option to `false` prevents the hooks from Bcc'ing
  AdaCore's mailing-list used to file all commits being made.
  :warning: **This option should never be used in any official
  repository, and is only meant to for testing of the git hooks
  outside of the testsuite.**

* **`hooks.debug-level`** (default value: **0**):

  Setting this debug option to a value higher than zero turns debugging
  traces on. The higher the value, the more verbose the traces.

Pre-commit Checks
-----------------

### "Revert" commits

In order to avoid unnecessary complications while reverting a commit
that is causing problems, all pre-commit checks (revision log, style
checks) are deactivated for commits created by "git revert".

Since there is no reliable feature that we can use to identify these
commits, the git-hooks rely on a heuristic instead, and look for a
pattern in the commit's revision log that gets automatically inserted by
the "git revert" command. In particular, at the moment, we look for the
following pattern:

```
This reverts commit
```

### Pre-commit Checks on the Revision History

The hooks verify that the revision histories of all new commits being
pushed comply with the rules defined below. This step is skipped for
any commit whose revision history contains the `no-rh-check` sequence.

Rules enforced on the revision logs:

* **Empty line after subject line**

  By convention, the first line of the revision history should always be
  the subject of the commit. If additional text is required, an empty line
  should be inserted between the subject and the rest of the revision
  history.

  ```
  YES:
        | The subject of my commit - no other explanation required

  YES:
        | The subject of my commit
        |
        | This is what this commit does.

  NO:
        | The subject of my commit
        | This is what this commit does, but an empty line is missing
        | between the subject and this description.
  ```

* **Maximum line length in revision history**

  See `hooks.max-rh-line-length` above.

* **Unedited revision history of merge commits**

  The purpose of this rule is to prevent a merge commit which was
  unintentionally created to be pushed to the shared repository. This
  can easily happen when, for instance, forgetting the `--rebase` option
  when doing a `git pull`.

  It works by detecting the default text that git uses as the revision
  history when the merge does not trigger a merge conflict.  When a merge
  was in fact intentional, the revision history of the merge commit must
  be manually edited to avoid the `Merge branch '[...]` line that git uses
  by default as the subject of the merge commit. Doing so will satisfy
  this pre-commit check.

  :information_source: Although strongly discouraged, this check can be
  disabled by setting the `hooks.disable-merge-commit-checks` config
  option to `true`.

* **Merge conflict section**

  When creating a merge commit during which conflicts were discovered
  and had to be resolved, the default revision history created by git and
  proposed for edition contains a section at the end that lists the files
  inside which merge conflicts where found. We do not want this section
  in the revision history of our commits, so the hooks verify that
  the author of the commit remembered to delete it.

* **Missing Ticket Number**

  This check is enable only if the `hooks.tn-required` config option
  is set.  For such repositories, the hooks verify that the revision
  log contains a Ticket Number.

  This requirement can be by-passed via the use of the word
  `no-tn-check` embedded in the revision log. Casing is not taken
  into account for this rule.

### Filename Collisions Pre-commit Check

On Operating Systems such as Darwin or Windows, where the File System
is typically case-insensitive, having two files whose name only differ
in the casing (Eg: `hello.txt` and `Hello.txt`, or `dir/hello.txt` vs
`DIR/hello.txt`) can cause a lot of confusion. To avoid this, the hooks
will reject any commit where such name collision occurs.

This check is disabled on the branches matching the `hooks.no-precommit-check`
config value.

### Pre-commit Checks on the Differences Introduced by the Commit

This is the usual "style check" performed by the `style_checker`
(see the `hooks.style-checker` config).

Note that the program verifies the entire contents of the files being
modified, not just the modified parts.

### Controlling the Pre-commit Checks

> :warning: Despite the use of very similar names, note the fairly
> important difference in scope between the `hooks.no-precommit-checks`
> config option, and the `no-precommit-check` git attribute! (see below)

By default, the pre-commit checks are turned on for all commits of all
branches. The following controls are available to tailor the hooks'
behavior regarding this check:

* The `hooks.no-precommit-check` config option can be used to turn
  pre-commit checks off entirely for a given branch. This option is
  typically used for branches tracking other branches from a third-party
  repository.

* If the `no-precommit-check` string is found anywhere in the revision
  log of that commit, *style* checks are turned off entirely for that
  commit only (all other precommit checks are preserved).

* Setting the `hooks.combined-style-checking` config option tells the
  hooks that the second part of the pre-commit checks (operating on the
  differences introduces by the commits) to only check the final result.
  Thus, if a user pushes an update introduces two new commits C1 and C2,
  it does not matter if C1 contains a style-check violation as long as
  the violation is corrected in C2.

  It is important to note, however, that the pre-commit checks on the
  revision histories are still performed on a commit-per-commit basis.
  Otherwise, it would be possible to push a commit missing a Ticket
  Number in repositories that are configured to require one.

* The `no-precommit-check` git attribute.

  Setting this attribute for any given file disables the pre-commit
  checks for this file. See `git --help attributes` for more info
  on how to set those attributes.

Email Notifications
-------------------

In general, developers are notified via email whenever a change
is pushed to the repository. This section describes the policy used
to determine which emails are being sent.

### The Summary Email

The purpose of this email is to give a quick overview of what has changed.

#### Composition

The Summary Email is composed of two sections:

1. A short description of what has changed.

   For instance, if a tag was created, it will explain what kind of tag
   was created, what the associated revision log was, and what commit it
   points to.

1. Optionally, a list of commits which have been lost and/or added.

#### Sending Policy

The general policy is to send the Summary Email for all updates in order
to inform its developers about the change. However, there are a number
of situations where the email would bring little information to the
Commit Emails already sent out:

* Branch updates:

  If the update does not cause any commit to be lost, nor does it
  include commits from a branch matching the `hooks.no-emails`
  configuration, then the email is superfluous and therefore not sent.

* Notes updates:

  Notes are really a special case of branch handling, where only
  fast-forward updates are allowed, and where the `hooks.no-emails`
  configuration is ignored. So the Summary Email is also never sent.

#### Filing Policy (AdaCore-specific)

Normally, this email is not used for filing purposes (ie, a copy is not
even sent to our filing email address), as we are more interested in
filing the individual commits than the summary.

However, it is interesting to file those emails in the following cases:

* tag creation
* tag update

In those cases, the revision log attached to those tags may contain
a TN, which means this event deserves filing.

In either case, a `Diff:` marker is always added before the section
summarizing the list of commits that were lost and/or added, making sure
that this part of the email never gets filed, as the commits themselves
are already getting filed.

### The Commit Emails

#### Composition

The subject of that email is the commit's subject and its contents is
roughly what the `git show` command would display.

#### Sending Policy

The Commit Email is always sent, unless the commit is found to exist
in a branch matching the `hooks.no-emails` configuration.

#### Filing Policy (AdaCore-specific)

This email is always bcc'd to AdaCore's filing email address.
Note that this list must not appear in any explicit To:/Cc: header,
as we want to prevent any replies from being sent there.

### Using a Script in hooks.mailinglist

For projects that want to use separate email addresses based on
a commit or the name of the reference being updated, it is possible
to use a script in place of an email address in the `hooks.mailinglist`
config.  Script entries are identified by the fact that the entry is
an **absolute filename**, and that this filename points to a file on
the server which is **an executable**.

:information_source: Note that the "term" script is used loosely here as,
although we expect most users of that feature to indeed use a script,
a compiled program would work just as well.

#### Script Calling Convention

This script is called by the hooks as follow:

* The list of files being changed is passed via standard input, one file
  per line (this list may be empty);

* The name of the reference being updated is passed as the script's
  first argument.

The hooks expects the script to return the list of email addresses on standard output, one email address per line.

By convention, we expect the scripts to return **all email addresses**
when the given list of files being changed is empty. This is useful
for "cover" emails that the hooks want to send to everyone.

#### Script Email Expansion Policy for Commit Emails

For commit emails, the hooks will call the mailinglist script with
the list of files being changed by the commit, and let the script decide
who should be notified based on that list of files.

#### Script Email Expansion Policy for Git Note Update Emails

Git Note Update emails are similar to Commit Emails, and therefore
the distribution list will be computed based on the list of files
being changed. The only difference is that the list of files is
going to be the list of files in the commit being annotated, not
the note's commit.

#### Script Email Expansion Policy for "Cover" Emails

The expansion policy for cover emails is currently very simple: Send
to everyone.

Rationale:

* Branch Updates:

  * For branch *creation and deletion*, it seems easy to understand how
    there is little way for us to determine who is interested in that
    branch update, unless we provide the name of the branch to the
    script. We might do that at some point, but keep things simple for
    now.

  * For branch *update*, if we have a cover letter, it means we have
    either commits already in another branch, or we're losing commits.
    Either should be relatively rare since merges are discouraged, and
    non-fast-forward changes are forbidden. So, it seems simple enough
    to send to everyone.

* Tags:

  Although it might be tempting to say to say that the notification
  should be same to the same list as the target's commit, this does not
  work: It is entirely possible that a tag for a given project point to a
  commit that only touches files for another project (Eg: a branchpoint
  tag, for instance). So, tags should be really treated the same as
  branches.

Managing External Baselines
---------------------------

It is very common to maintain forks of repositories which are officially
maintained elsewhere. Typically, what we would be doing is maintain
one's own fork of the official repository, to which we then apply
our own set of changes.

Since we do not want style checking, nor emails when importing a new
branch from the official repositories, the procedure provided below
should be followed. It assumes the following one-time configuration of
the repository's git-hooks configuration:

* Choose a convention for naming the branches which will be exact copies
  of the branches in the official repository (Eg: branches whose name
  start with "official/", or "fsf-", etc).

* Configure the git-hooks to turn emails and precommit checks off for
  those branches. Eg:

  ```
      # By convention, all branches whose name start with "official/"
      # (Eg: official/master), are considered branches from the official
      # repository.
      no-emails = refs/heads/official/.*
      no-precommit-check = refs/heads/official/.*
  ```

Once the setup above is done (only needs to be done once), the following
procedure should work. Let's assume for instance that you would like to
important branch `release-xyz` from the official repository. Locally,
your own clone should have two remotes:

* One remote pointing to your fork;

* One remote pointing to the official repository.

We will assume that the remote pointing to your fork is called
`origin`, and that the one pointing to the official repository
is called `upstream`.

We will also assume that the convention you have chosen for the official
branches is that they all start with `official/`, followed by the official
branch name. So, in our example, in our fork, we would call this branch
`official/release-xyz`.

From your repository:

* Fetch from the official repository the branch you want to import;

  ```console
  $ git fetch upstream release-xyz
  ```

* Next, push to that branch to your fork, exactly as is (untouched),
  but following the naming convention we chose for it:

  ```console
  $ git push origin upstream/release-xyz:refs/heads/official/release-xyz
  ```

  You will see a message warning you that this branch has been
  configured to not trigger commit emails. This is what you want.

* Then, create the branch that you will be using in your fork,
  and push it.

  ```console
  $ git branch release-xyz origin/official/release-xyz
  $ git push origin release-xyz
  ```

From there, use the `release-xyz` branch as you normally would.

Later on, if you need to import new changes that were made in
the official repository's `release-xyz` branch, follow the same
principle, but without having to create the `release-xyz` branch
in the fork.  Make sure that your (fork's) `release-xyz` branch
is up to date, before doing the import, however.

* Fetch the latest changes for your branch and push it to the fork:

  ```console
  $ git fetch upstream release-xyz
  $ git push origin upstream/release-xyz:official/release-xyz
  ```

* Then, switch to the fork's `release-xyz` branch, merge the changes
  from the official `release-xyz` branch, and then push:

  ```console
  $ git checkout release-xyz
  $ git merge upstream/release-xyz
  $ git push origin release-xyz
  ```

Retiring Old Branches
---------------------

The recommended method for retiring a branch which is no longer useful
is to add a `hooks.frozen-ref` in the project's project.config file
which lists the branch's reference name. Eg:

```
[hooks]
    frozen-ref = refs/heads/gdb-7.5
```

Alternatively, the following (legacy) method is also available:

* Create a tag referencing the tip of the branch to be retired.

  The tag name should be `retired/<branch-name>` where `<branch-name>`
  is the name of the branch to be retired.

* Push this tag to the official repository;

* Delete the retired branch in the official repository.

By using the naming suggested for the tag, **the hooks will ensure that
the branch never gets accidently recreated**. This would otherwise happen
if a developer did not know that the branch was deleted, still had that
branch locally in his repository, and tried to push his change as usual.

The use of the `retired/` namespace for those tags also helps
standardizing the location where those tags are created.

And the use of a tag allows everyone to determine the latest state of
that branch prior to its retirement.

Re-Sending the Commit Emails
----------------------------

In the situation where the commit emails were either not sent, or lost,
the following procedure should allow the emails to be sent again.
It simply consists in calling the post-receive script with the right
environment and arguments, which emulates the hooks action at the end
of a "push".

One of the issues is that the author of the commit and the author of
the email are two distinct pieces of information. Many times, the two
will be the same, but not always. For the emails, the author is normally
the user who is doing the push (that is, the user calling the hooks),
while the author of the commit is provided as one of the elements of
the commit email data. But he information about the author of the push
is lost after the push has completed, and thus cannot be inferred again.

When re-sending the commit emails, we should try as much as possible
to use the correct email address as the sender, which means overriding
the default sender. If there is one principal developer who did most of
the pushes, you can override the default email sender by using the
`--submitter-email` option when calling post-receive. See how
this option can be used in the example below.

Another option for overriding the default sender's email address
which does not require the use of the command-line option is to define
the following environment variables accordingly with their Unix user ID
and full name:

```console
$ export GIT_HOOKS_USER_NAME=ds
$ export GIT_HOOKS_USER_FULL_NAME='Dave Smith'
```

If none of these two alternatives for overriding the sender's email
address, the user performing this procedure will be used as author of
the commit emails.

Unless the missing emails are re-sent very shortly after they were
pushed, it is recommended to ask the hooks to add a warning banner
in the emails being sent that the emails were manually re-sent.
To do so, define the following environment variable, using the reason
for resending:

```console
$ export GIT_HOOKS_EMAIL_REPLAY_REASON="<short reason> (XXXX-XXX)"
```

Assuming that we want to send emails for the commit in the range
`SHA1_BEFORE..SHA1_AFTER` and that `BRANCH_NAME` is the name of
the branch containing those commits, the following command should
do the trick:

```console
$ cd /scmrepos/git/<git-repo>
$ echo "SHA1_BEFORE SHA1_AFTER refs/heads/BRANCH_NAME" | \
    ./hooks/post-receive --submitter-email='Dave Smith <ds@example.com>'
```

If you would like to do a dry-run before actually getting the emails
sent, you can force the script into testsuite mode, which will cause
emails to be printed on standard output rather than actually be sent:

```console
# Ask the testsuite to use our fake sendmail program instead of the system one.
# This fake sendmail will dump the email on stdout rather than actually send
# the email.
$ export GIT_HOOKS_SENDMAIL=/path/to/git-hooks/testsuite/bin/stdout-sendmail

# Ask the testsuite to stop redirecting stdout, so we can see the emails
# being dumped by our fake sendmail above.
$ export GIT_HOOKS_TESTSUITE_MODE=true
```

Once satisfied with the output, simply unset the environment variables
above before re-running the same post-receive command above again.
