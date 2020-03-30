from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_nonexistant(self):
        """Try deleting a references that don't exist on the remote."""
        cd('%s/repo' % TEST_DIR)

        p = Run('git push origin :does-not-exist'.split())
        expected_out = """\
error: unable to delete 'does-not-exist': remote ref does not exist
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Do the same as above, but using the full reference, instead
        # of using the branch name.

        p = Run('git push origin :refs/heads/does-not-exist'.split())
        expected_out = """\
remote: *** unable to delete 'refs/heads/does-not-exist': remote ref does not exist
remote: error: hook declined to update refs/heads/does-not-exist
To ../bare/repo.git
 ! [remote rejected] does-not-exist (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Same as above, but using the full reference in the tags
        # namespace.

        p = Run('git push origin :refs/tags/does-not-exist'.split())
        expected_out = """\
remote: *** unable to delete 'refs/tags/does-not-exist': remote ref does not exist
remote: error: hook declined to update refs/tags/does-not-exist
To ../bare/repo.git
 ! [remote rejected] does-not-exist (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Same as above, but using the full reference in the notes
        # namespace.

        p = Run('git push origin :refs/notes/commits'.split())
        expected_out = """\
remote: *** unable to delete 'refs/notes/commits': remote ref does not exist
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
