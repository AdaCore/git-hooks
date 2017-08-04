from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.

        The commit contains one file rename, but we tell the hooks
        to treat renames as a new file, and thus expect to apply
        the pre-commit checks on the new file.
        """
        cd ('%s/repo' % TEST_DIR)

        self.set_debug_level(2)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=a60540361d47901d3fe254271779f380d94645f7, new_rev=6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote: DEBUG: validate_ref_update (refs/heads/master, a60540361d47901d3fe254271779f380d94645f7, 6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote: DEBUG: update base: a60540361d47901d3fe254271779f380d94645f7
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=a60540361d47901d3fe254271779f380d94645f7, new_rev=6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote:   DEBUG: deleted file ignored: a
remote: *** pre-commit check failed for commit: 6a48cdab9b100506a387a8398af4751b33a4bfd0
remote: *** cvs_check: `repo' < `b'
remote: *** ERROR: b: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertTrue(p.status != 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
