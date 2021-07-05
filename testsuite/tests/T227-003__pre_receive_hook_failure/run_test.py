import os

from support import *


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master."""
        # First, adjust the project.config file to use a pre-receive-hook
        # script.  We can't do it any earlier, because we don't know
        # which temporary directory will be used when running this test.
        p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
        assert p.status == 0, p.image

        p = testcase.run(["git", "checkout", "FETCH_HEAD"])
        assert p.status == 0, p.image

        p = testcase.run(
            [
                "git",
                "config",
                "-f",
                "project.config",
                "--add",
                "hooks.pre-receive-hook",
                os.path.join(testcase.work_dir, "pre-receive-hook"),
            ]
        )
        assert p.status == 0, p.image

        p = testcase.run(
            [
                "git",
                "commit",
                "-m",
                "add hooks.pre-receive-hook config",
                "project.config",
            ]
        )
        assert p.status == 0, p.image

        p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
        assert p.status == 0, p.image

        # Push master to the `origin' remote.  The pre-receive-hook
        # should be called (as evidenced by some debug output it prints),
        # and it should reject the update.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** Update rejected by this repository's hooks.pre-receive-hook script
remote: *** ({testcase.work_dir}/pre-receive-hook):
remote: *** -----[ pre-receive-hook args ]-----
remote: *** -----[ pre-receive-hook stdin ]-----
remote: *** d065089ff184d97934c010ccd0e7e8ed94cb7165 a60540361d47901d3fe254271779f380d94645f7 refs/heads/master
remote: *** -----[ pre-recieve-hook end ]-----
remote: *** A clear error message explaining why this change is not allowed.
To ../bare/repo.git
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
            testcase=testcase
        )

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
