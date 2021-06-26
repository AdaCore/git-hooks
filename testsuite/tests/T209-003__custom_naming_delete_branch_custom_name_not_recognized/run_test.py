from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_branch_custom_name_not_recognized(testcase):
        """Push a branch deletion using a custom reference name."""
        cd('%s/repo' % TEST_DIR)

        # Try to delete a reference which does exist in the remote
        # but has a name which does not match any of the known
        # namespaces (meaning we cannot determine the kind of
        # reference this is, be it a branch, or a tag, or maybe
        # a reference to some git notes).

        p = Run('git push origin :refs/others/exists-but-unrecognized'
                .split())
        expected_out = """\
remote: *** Unable to determine the type of reference for: refs/others/exists-but-unrecognized
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
remote: error: hook declined to update refs/others/exists-but-unrecognized
To ../bare/repo.git
 ! [remote rejected] refs/others/exists-but-unrecognized (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Try to delete a reference which both has a name that does not
        # match any of the known namespaces, and does not even exist
        # in the remote repository.

        p = Run('git push origin :refs/does-not-exist/my-feature'
                .split())
        expected_out = """\
remote: *** unable to delete 'refs/does-not-exist/my-feature': remote ref does not exist
remote: error: hook declined to update refs/does-not-exist/my-feature
To ../bare/repo.git
 ! [remote rejected] refs/does-not-exist/my-feature (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()

