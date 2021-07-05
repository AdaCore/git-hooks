from support import *


class TestRun(TestCase):
    def test_push_commit_on_before(testcase):
        """Try pushing before..."""
        p = testcase.run("git push origin before".split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit 5ce0f27c332ee6c88517ff79d0fdb935fda42cd4
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/before
To ../bare/repo.git
 ! [remote rejected] before -> before (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_commit_on_after(testcase):
        """Try pushing after..."""
        p = testcase.run("git push origin after".split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit 642e62b7dd11c9263d7db852ce2752d988ec7243
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/after
To ../bare/repo.git
 ! [remote rejected] after -> after (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
