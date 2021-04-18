from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_create_branch_custom_name_not_recognized(self):
        """Create a new branch with a custom reference name.

        This reference name is not recognized as a branch by
        the repository's naming scheme, and so the update should
        be rejected.
        """
        cd('%s/repo' % TEST_DIR)

        p = Run('git push origin master:refs/does-not-exist/my-feature'
                .split())
        expected_out = """\
remote: *** Unable to determine the type of reference for: refs/does-not-exist/my-feature
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/.*
remote: ***       refs/meta/.*
remote: ***       refs/drafts/.*
remote: ***       refs/for/.*
remote: ***       refs/publish/.*
remote: ***       refs/vendor/.*
remote: ***       refs/user/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/tags/.*
remote: error: hook declined to update refs/does-not-exist/my-feature
To ../bare/repo.git
 ! [remote rejected] master -> refs/does-not-exist/my-feature (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
