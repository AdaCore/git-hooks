from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin meta/config:refs/meta/config'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Add small comment.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 87a3fc391a712ee33e313fad7dee60073dd46a52
remote: X-Git-Newrev: 8be147281032266bc1287e30072c54e2942e09e8
remote:
remote: commit 8be147281032266bc1287e30072c54e2942e09e8
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
remote: index e565530..73f544e 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,4 +1,5 @@
remote:  [hooks]
remote: +        # Standard minimum configuration.
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
remote:          filer-email = filer@example.com
To ../bare/repo.git
   87a3fc3..8be1472  meta/config -> refs/meta/config
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
