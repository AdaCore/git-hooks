from support import *


class TestRun(TestCase):
    def test_push_branch_with_merge_commit(testcase):
        """Test merge-commit reject on branches where they are not allowed.

        The extra "trick" here, comes from the fact that the merge commit
        has a revision log which makes it look like the file is a revert,
        which might tempt the git-hooks to skip all checks (including
        the check against merge commits) and thus incorrectly allowing
        this commit.
        """
        cd("%s/repo" % TEST_DIR)

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** Merge commits are not allowed on refs/heads/master.
remote: *** The commit that caused this error is:
remote: ***
remote: ***     commit fed85d780821e42879e5dc7d03411cfd0cc70e9a
remote: ***     Subject: Merge topic branch fsf-head.
remote: ***
remote: *** Hint: Consider using "git cherry-pick" instead of "git merge",
remote: ***       or "git pull --rebase" instead of "git pull".
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
