from support import *
from subprocess import check_output, check_call

class TestRun(TestCase):
    def __bare_repo_fixup(self):
        """Fix the bare repository to implement legacy hooks configuration.

        Reproduce the (legacy) situation where the project.config file
        in refs/meta/config does not exist, and where the repository's
        hooks configuration is stored inside the repository's config
        file.
        """
        # First, extract the configuration, available at the standard
        # location.
        cfg_txt = check_output(
            'git show refs/meta/config:project.config'.split(),
            cwd='%s/bare/repo.git' % TEST_DIR)
        with open('%s/bare/repo.git/config' % TEST_DIR, 'a') as f:
            f.write(cfg_txt)
        check_call('git update-ref -d refs/meta/config'.split(),
                   cwd='%s/bare/repo.git' % TEST_DIR)

    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        self.__bare_repo_fixup()

        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** -----------------------------------------------------------------
remote: *** Unable to find the file project.config in refs/meta/config.
remote: ***
remote: *** Your repository appears to be incorrectly set up. Please contact
remote: *** your repository's administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
To ../bare/repo.git
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
