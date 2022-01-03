def test_push_tag(testcase):
    """Try pushing a new value for an annotated tag."""
    # Push "full-tag". The repository has been configured to
    # ignore the standard namespace for tags, so this should be
    # rejected as "not recognized".

    p = testcase.run("git push --force origin full-tag".split())
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/tags/full-tag
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/.*
remote: ***       refs/meta/.*
remote: ***       refs/drafts/.*
remote: ***       refs/for/.*
remote: ***       refs/publish/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/vendor/.*/tags/.*
remote: ***       refs/user/.*/tags/.*
remote: error: hook declined to update refs/tags/full-tag
To ../bare/repo.git
 ! [remote rejected] full-tag -> full-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Push "full-tag" to a reference which already exists in
    # the remote and is recognized as a tag.

    p = testcase.run(
        "git push --force origin" " full-tag:refs/user/myself/tags/full-tag".split()
    )
    expected_out = """\
remote: *** ---------------------------------------------------------------
remote: *** --  IMPORTANT NOTICE:
remote: *** --
remote: *** --  You just updated the tag 'myself/tags/full-tag' in namespace 'refs/user' as follow:
remote: *** --    old SHA1: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: *** --    new SHA1: 17b9d4acf8505cd1da487ad62e37819b93779a27
remote: *** --
remote: *** -- Other developers pulling from this repository will not
remote: *** -- get the new tag. Assuming this update was deliberate,
remote: *** -- notifying all known users of the update is recommended.
remote: *** ---------------------------------------------------------------
remote: *** cvs_check: `repo' < `bar.c' `foo'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Updated tag 'myself/tags/full-tag' in namespace 'refs/user'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/user/myself/tags/full-tag
remote: X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: X-Git-Newrev: 17b9d4acf8505cd1da487ad62e37819b93779a27
remote:
remote: The signed tag 'myself/tags/full-tag' in namespace 'refs/user' was updated to point to:
remote:
remote:  8c0b415... Added bar.c, and updated foo.
remote:
remote: It previously pointed to:
remote:
remote:  354383f... Initial commit.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Thu Jun 28 11:50:36 2012 -0700
remote:
remote:     Tag a commit that makes more sense.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   8c0b415... Added bar.c, and updated foo.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/user/myself/tags/full-tag)] Added bar.c, and updated foo.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/user/myself/tags/full-tag
remote: X-Git-Oldrev: 354383fa06047ef8053782410c221341e4b07ec4
remote: X-Git-Newrev: 8c0b4151f9f41efcaeb70ea6f91158e4605aaeda
remote:
remote: commit 8c0b4151f9f41efcaeb70ea6f91158e4605aaeda
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Jun 28 11:24:42 2012 -0700
remote:
remote:     Added bar.c, and updated foo.
remote:
remote: Diff:
remote: ---
remote:  bar.c | 2 ++
remote:  foo   | 1 +
remote:  2 files changed, 3 insertions(+)
remote:
remote: diff --git a/bar.c b/bar.c
remote: new file mode 100644
remote: index 0000000..2fcb2a3
remote: --- /dev/null
remote: +++ b/bar.c
remote: @@ -0,0 +1,2 @@
remote: +/* Some globals.  */
remote: +int global_bar = 0;
remote: diff --git a/foo b/foo
remote: index e69de29..bac6ca8 100644
remote: --- a/foo
remote: +++ b/foo
remote: @@ -0,0 +1 @@
remote: +Added file bar.c
To ../bare/repo.git
   a69eaab..17b9d4a  full-tag -> refs/user/myself/tags/full-tag
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Push "full-tag" to a reference which already exists in
    # the remote but is not recognized as a tag.

    p = testcase.run(
        "git push --force origin" " full-tag:refs/nogo/myself/tags/full-tag".split()
    )
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/nogo/myself/tags/full-tag
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/.*
remote: ***       refs/meta/.*
remote: ***       refs/drafts/.*
remote: ***       refs/for/.*
remote: ***       refs/publish/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/vendor/.*/tags/.*
remote: ***       refs/user/.*/tags/.*
remote: error: hook declined to update refs/nogo/myself/tags/full-tag
To ../bare/repo.git
 ! [remote rejected] full-tag -> refs/nogo/myself/tags/full-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
