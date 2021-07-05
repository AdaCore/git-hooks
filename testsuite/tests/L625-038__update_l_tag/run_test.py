from support import *


class TestRun(TestCase):
    def test_delete_lightweight_tag(testcase):
        """Try updating a lightweight tag."""
        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        testcase.set_debug_level(1)

        p = testcase.run("git push --force origin some-tag".split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/some-tag, 8b9a0d6bf08d7a983affbee3c187adadaaedec9e, 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5)
remote: *** ---------------------------------------------------------------
remote: *** --  IMPORTANT NOTICE:
remote: *** --
remote: *** --  You just updated the tag 'some-tag' as follow:
remote: *** --    old SHA1: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: *** --    new SHA1: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote: *** --
remote: *** -- Other developers pulling from this repository will not
remote: *** -- get the new tag. Assuming this update was deliberate,
remote: *** -- notifying all known users of the update is recommended.
remote: *** ---------------------------------------------------------------
remote: DEBUG: update base: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=8b9a0d6bf08d7a983affbee3c187adadaaedec9e, new_rev=8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5)
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: post_receive_one(ref_name=refs/tags/some-tag
remote:                         old_rev=8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote:                         new_rev=8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5)
remote: DEBUG: update base: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@example.com>
remote: To: something-ci@example.com
remote: Subject: [repo] Updated tag 'some-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/tags/some-tag
remote: X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: X-Git-Newrev: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote:
remote: The lightweight tag 'some-tag' was updated to point to:
remote:
remote:  8a567a0... Put some contents in file `a'.
remote:
remote: It previously pointed to:
remote:
remote:  8b9a0d6... New file: a.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   8a567a0... Put some contents in file `a'.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@example.com>
remote: To: something-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/some-tag] Put some contents in file `a'.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/tags/some-tag
remote: X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: X-Git-Newrev: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote:
remote: commit 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Jun 25 15:10:13 2012 -0700
remote:
remote:     Put some contents in file `a'.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index e69de29..4b29465 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -0,0 +1 @@
remote: +Put some contents in.
To ../bare/repo.git
 + 8b9a0d6...8a567a0 some-tag -> some-tag (forced update)
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
