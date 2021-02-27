from support import cd, Run, runtests, TestCase, TEST_DIR


class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Push the refs/notes/review note."""
        cd('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin refs/notes/review:refs/notes/review'.split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/notes/review',
remote: --  which matches the name of the reference being updated
remote: --  (refs/notes/review).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   35631ec..a9e9519  refs/notes/review -> refs/notes/review
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
