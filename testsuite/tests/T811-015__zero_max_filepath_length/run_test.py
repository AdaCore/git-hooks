from support import *

class TestRun(TestCase):
    def test_push_commits(self):
        """Test setting hooks.max-filepath-length to zero turns check off."""

        # The purpose of this testcase is to verify that, when setting
        # the hooks.max-filepath-length config to zero, the corresponding
        # checks get turned off.
        #
        # In order to do so, we first need to make sure that there is
        # such a check in place by trying to push a commit which
        # violates this policy. This is the first part of this testcase.
        # Once this is verified, we set this config option to zero,
        # and try again. Once the config is set to zero, the same commit
        # that was previously rejected should now be accepted, proving
        # that the length check is no longer applied.

        cd ('%s/repo' % TEST_DIR)

        # For this testcase, the contents of the emails being sent
        # is not important, so reduce their verbosity.
        self.change_email_sending_verbosity(full_verbosity=False)

        #################################################################
        #
        #  Create a new commit which introduces a new file whose path
        #  length exceeds the default maximum.
        #
        #  We do this programatically so as facilitate future adjustments
        #  of this testcase should the default actually change (instead of
        #  having to redo the commit in the test repository, we simply
        #  change a constant below).
        #
        #################################################################

        # A constant indicating the length of the name of a new file
        # we will try to push to the repository. This constant should
        # be greater than the hooks's default.

        TEST_FILE_PATH_LENGTH = 160

        new_file_name = 'a' * TEST_FILE_PATH_LENGTH
        with open(new_file_name, 'w') as f:
            f.write("Hello world\n");

        p = Run(["git", "add", new_file_name])
        assert p.status == 0, p.image

        p = Run(["git", "commit", "-m", "Add looooong file"])
        assert p.status == 0, p.image

        # Determine the SHA1 of that new commit. We will need it later
        # when matching outputs...

        p = Run(["git", "log", "-1", "--format=%H"])
        assert p.status == 0, p.image
        new_commit_sha1 = p.out.strip()

        p = Run(["git", "log", "-1", "--format=%h"])
        assert p.status == 0, p.image
        new_commit_abbrev_sha1 = p.out.strip()

        #################################################################
        #
        #  Try to push that commit; it should be rejected because
        #  of the file's length.
        #
        #################################################################

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** The following commit introduces some new files whose total
remote: *** path length exceeds the maximum allowed for this repository.
remote: *** Please re-do your commit choosing shorter paths for those new
remote: *** files, or contact your repository administrator if you believe
remote: *** the limit should be raised.
remote: ***
remote: ***     Commit: {new_commit_sha1}
remote: ***     Subject: Add looooong file
remote: ***
remote: *** The problematic files are (150 characters max):
remote: ***
remote: ***     {new_file_name} ({TEST_FILE_PATH_LENGTH} characters)
remote: ***
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(new_commit_sha1=new_commit_sha1,
           new_file_name=new_file_name,
           TEST_FILE_PATH_LENGTH=TEST_FILE_PATH_LENGTH)

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        #################################################################
        #
        #  Change the repository's hooks.max-filepath-length configuration
        #  by setting it to zero. This should disable the max file path
        #  length checks, which we will verify by trying to push our commit
        #  again, expecting the commit to be accepted, this time.
        #
        #################################################################

        p = Run(['git', 'fetch', 'origin', 'refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'checkout', 'FETCH_HEAD'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'config', '--file', 'project.config',
                 'hooks.max-filepath-length', '0'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'commit', '-m', 'Set hooks.max-filepath-length to 0',
                 'project.config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert 'HEAD -> refs/meta/config' in p.out.splitlines()[-1], p.image

        p = Run(['git', 'checkout', 'master'])
        self.assertEqual(p.status, 0, p.image)

        #################################################################
        #
        #  Try to push that commit; it should no longer be rejected
        #  despite the new file's length.
        #
        #################################################################

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: Sending email: [repo] Add looooong file...
To ../bare/repo.git
   8d5ce43..{new_commit_abbrev_sha1}  master -> master
""".format(new_commit_abbrev_sha1=new_commit_abbrev_sha1)

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
