from support import *

class TestRun(TestCase):
    def test_push_github_pull_19(self):
        """Try pushing the branch named "github/pull/19"
        """
        cd ('%s/repo' % TEST_DIR)

        # This branch contains a .gitreview whose defaultbranch setting
        # points to another branch name. So normally, the hooks should
        # reject this update, asking for the config to be changed instead.
        # However, the repository has been configured to allow updates
        # for branches whose name start with "github/pull/", so we expect
        # the push to be accepted.

        p = Run('git push origin github/pull/19'.split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/github/pull/.*',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/github/pull/19).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
 * [new branch]      github/pull/19 -> github/pull/19
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
