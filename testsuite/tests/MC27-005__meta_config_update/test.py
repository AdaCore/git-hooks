from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin meta/config:refs/meta/config'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/project.config'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo(refs/meta/config)] Add small comment.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 85d4247731f5fb93305b733053bc7e2c665f2fb5
remote: X-Git-Newrev: fe3f0147873852f46b6fc0c372fbe846367055d5
remote:
remote: commit fe3f0147873852f46b6fc0c372fbe846367055d5
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 30 08:04:51 2013 +0400
remote:
remote:     Add small comment.
remote:
remote: Diff:
remote: ---
remote:  project.config | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/project.config b/project.config
remote: index 93a508c..bd12a75 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,3 +1,4 @@
remote:  [hooks]
remote: +        # Standard minimum configuration.
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
To ../bare/repo.git
   85d4247..fe3f014  meta/config -> refs/meta/config
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
