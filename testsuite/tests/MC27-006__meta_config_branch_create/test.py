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
        """Test creating the refs/meta/config branch on the remote.
        """
        self.__bare_repo_fixup()

        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin meta/config:refs/meta/config'.split())
        expected_out = """\
remote: *** -----------------------------------------------------------------
remote: *** Unable to find file project.config from branch refs/meta/config
remote: *** Using your repository's config file instead.
remote: ***
remote: *** This is not a fatal issue, but please contact your repository's
remote: *** administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
remote: *** -----------------------------------------------------------------
remote: *** Unable to find file project.config from branch refs/meta/config
remote: *** Using your repository's config file instead.
remote: ***
remote: *** This is not a fatal issue, but please contact your repository's
remote: *** administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'config' in namespace 'refs/meta'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 85d4247731f5fb93305b733053bc7e2c665f2fb5
remote:
remote: The branch 'config' was created in namespace 'refs/meta' pointing to:
remote:
remote:  85d4247... Initial config for project
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo(refs/meta/config)] Initial config for project
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev:
remote: X-Git-Newrev: 85d4247731f5fb93305b733053bc7e2c665f2fb5
remote:
remote: commit 85d4247731f5fb93305b733053bc7e2c665f2fb5
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Dec 27 15:32:11 2013 +0400
remote:
remote:     Initial config for project
remote:
remote: Diff:
remote: ---
remote:  project.config | 3 +++
remote:  1 file changed, 3 insertions(+)
remote:
remote: diff --git a/project.config b/project.config
remote: new file mode 100644
remote: index 0000000..93a508c
remote: --- /dev/null
remote: +++ b/project.config
remote: @@ -0,0 +1,3 @@
remote: +[hooks]
remote: +        from-domain = adacore.com
remote: +        mailinglist = git-hooks-ci@example.com
To ../bare/repo.git
 * [new branch]      meta/config -> refs/meta/config
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
