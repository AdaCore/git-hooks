from support import *


class TestRun(TestCase):
    def test_push(testcase):
        """Try pushing master..."""
        cd("%s/repo" % TEST_DIR)

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit dc858ec25d5afed3fc296a56aa9a2c3101991859
remote: *** Subject: Minority update.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
