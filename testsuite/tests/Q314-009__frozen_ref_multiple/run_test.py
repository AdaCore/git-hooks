from support import *

class TestRun(TestCase):
    def test_push_retired_branch(testcase):
        """Try pushing a branch update on a frozen branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin gdb-7.5'.split())

        assert p.status != 0, p.image

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed because
remote: *** this branch is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        testcase.assertRunOutputEqual(p, expected_out)

    def test_force_push_retired_branch(testcase):
        """Try force-pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push -f origin gdb-7.5'.split())

        assert p.status != 0, p.image

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed because
remote: *** this branch is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_other_frozen_branch(testcase):
        """Try pushing another branch which is also frozen
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin gdb-7.6'.split())
        expected_out = """\
remote: *** Updates to the gdb-7.6 branch are no longer allowed because
remote: *** this branch is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/heads/gdb-7.6
To ../bare/repo.git
 ! [remote rejected] gdb-7.6 -> gdb-7.6 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_master(testcase):
        """Try pushing master, which is not frozen
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin master'.split())
        expected_out = """\
Everything up-to-date
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_frozen_tag(testcase):
        """Try pushing a tag which has a "frozen-ref" entry.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin gdb-7.5-release'.split())
        expected_out = """\
remote: *** Updates to refs/tags/gdb-7.5-release are no longer allowed because
remote: *** this reference is now frozen (see "hooks.frozen-ref" in file
remote: *** project.config, from the special branch refs/meta/config).
remote: error: hook declined to update refs/tags/gdb-7.5-release
To ../bare/repo.git
 ! [remote rejected] gdb-7.5-release -> gdb-7.5-release (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_ok_tag(testcase):
        """Try pushing a tag which does not have a frozen-ref entry.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin gdb-7.6-release'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Created tag 'gdb-7.6-release'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/gdb-7.6-release
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 286ac09430628d1c8f1b2d32e871e0ad418da76d
remote:
remote: The unsigned tag 'gdb-7.6-release' was created pointing to:
remote:
remote:  a605403... Updated a.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Sun Jul 2 11:27:14 2017 -0700
remote:
remote:     tagging the gdb-7.6 release
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   a605403... Updated a.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/gdb-7.6-release] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/tags/gdb-7.6-release
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
 * [new tag]         gdb-7.6-release -> gdb-7.6-release
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
