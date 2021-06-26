from support import *
from os import environ

class TestRun(TestCase):
    def test_push_too_many_new_commits_on_master(testcase):
        """Try pushing too many new commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Change the HOME environment variable to TEST_DIR, to get
        # the hooks to look for the .no_cvs_check file there,
        # instead of the real HOME dir.
        environ['HOME'] = TEST_DIR

        # Create an empty .no_cvs_check file in the new HOME,
        # to disable pre-commit checks.
        no_cvs_check_fullpath = '%s/.no_cvs_check' % TEST_DIR
        open(no_cvs_check_fullpath, 'w').close()

        # Push master to the `origin' remote.  The remote should
        # reject it saying that there are too many new commits.
        # The goal is to verify that the no-cvs-check override
        # did not cause the max-commit-emails check to be skipped.
        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** This update introduces too many new commits (4), which would
remote: *** trigger as many emails, exceeding the current limit (3).
remote: *** Contact your repository adminstrator if you really meant
remote: *** to generate this many commit emails.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)



if __name__ == '__main__':
    runtests()
