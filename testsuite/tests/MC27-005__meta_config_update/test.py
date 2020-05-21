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
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Add small comment.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 674ac9d040601e16e4bc46fb8928398157c01232
remote: X-Git-Newrev: 86eb705b95540efd0d2f303688098de8babc457a
remote:
remote: commit 86eb705b95540efd0d2f303688098de8babc457a
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
remote: index 05e3cbe..d0c3607 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,4 +1,5 @@
remote:  [hooks]
remote: +        # Standard minimum configuration.
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
remote:  	filer-email = filer@example.com
To ../bare/repo.git
   674ac9d..86eb705  meta/config -> refs/meta/config
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
