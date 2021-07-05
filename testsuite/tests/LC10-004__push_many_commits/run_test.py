from support import *


class TestRun(TestCase):
    def test_push_too_many_new_commits_on_master(testcase):
        """Try pushing too many new commits on master."""
        # Push master to the `origin' remote.  The remote should
        # reject it saying that there are too many new commits.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/master',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/master).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   d065089..4ca9852  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
