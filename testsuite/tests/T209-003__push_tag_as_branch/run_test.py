from support import TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_push_tag_using_branch_reference_name(testcase):
        """Try pushing a tag as if it was a branch.

        Excercise the scenario where a user is trying to push a tag
        using a reference whose name indicates that this is a branch.
        This is a bit far-fetched in most cases, but might be less so
        in repositories that start using their own naming scheme.
        We want to make sure we handle these situations gracefullly
        in any case.
        """
        cd('%s/repo' % TEST_DIR)

        # Push refs/tags/v1, which is a tag, to a reference whose name
        # suggests it is a branch. We should get an error.
        p = testcase.run('git push origin refs/tags/v1:refs/heads/v1'.split())
        expected_out = """\
remote: *** This type of update (refs/heads/v1,tag) is not valid.
remote: error: hook declined to update refs/heads/v1
To ../bare/repo.git
 ! [remote rejected] v1 -> v1 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
