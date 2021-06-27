from support import *


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master."""
        cd("%s/repo" % TEST_DIR)

        # Push master to the `origin' remote.
        # The update should be refused because hooks.from-domain config
        # is not set.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** Error: hooks.from-domain config variable not set.
remote: *** Please contact your repository's administrator.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
