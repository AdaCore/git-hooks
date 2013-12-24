from support import *

class TestRun(TestCase):
    def test_push_tag(self):
        """Try pushing a new value for an annotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(1)

        # Push "full-tag". This tag has a new value, different from
        # that is on the remote.  We should get an email notification,
        # and a warning about how bad it is to do that.
        p = Run('git push --force origin full-tag'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/full-tag, a69eaaba59ea6d7574a9c5437805a628ea652c8e, 17b9d4acf8505cd1da487ad62e37819b93779a27)
remote: *** ---------------------------------------------------------------
remote: *** --  IMPORTANT NOTICE:
remote: *** --
remote: *** --  You just updated the "full-tag" tag as follow:
remote: *** --    old SHA1: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: *** --    new SHA1: 17b9d4acf8505cd1da487ad62e37819b93779a27
remote: *** --
remote: *** -- Other developers pulling from this repository will not
remote: *** -- get the new tag. Assuming this update was deliberate,
remote: *** -- notifying all known users of the update is recommended.
remote: *** ---------------------------------------------------------------
remote: DEBUG: update base: 354383fa06047ef8053782410c221341e4b07ec4
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=354383fa06047ef8053782410c221341e4b07ec4, new_rev=8c0b4151f9f41efcaeb70ea6f91158e4605aaeda)
remote: *** cvs_check: `trunk/repo/bar.c'
remote: *** cvs_check: `trunk/repo/foo'
remote: DEBUG: post_receive_one(ref_name=refs/tags/full-tag
remote:                         old_rev=a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote:                         new_rev=17b9d4acf8505cd1da487ad62e37819b93779a27)
remote: DEBUG: update base: 354383fa06047ef8053782410c221341e4b07ec4
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated tag full-tag
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/tags/full-tag
remote: X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: X-Git-Newrev: 17b9d4acf8505cd1da487ad62e37819b93779a27
remote:
remote: The signed tag 'full-tag' was updated to point to:
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
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/full-tag] Added bar.c, and updated foo.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/tags/full-tag
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
 + a69eaab...17b9d4a full-tag -> full-tag (forced update)
"""

        self.assertEqual(p.status, 0, p.image)
        # The expected output matches the output for git version 1.8.3.2.
        # For older versions of git, and in particular version 1.7.11.5,
        # the output is slightly different.  Upgrade the actual output
        # to pretend we got the new one.
        p.out = p.out.replace(
            '   a69eaab..17b9d4a  full-tag -> full-tag',
            ' + a69eaab...17b9d4a full-tag -> full-tag (forced update)')
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
