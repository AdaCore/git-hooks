from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin topic/new-feature'.split())
        expected_out = """\
remote: *** !!! WARNING: This is *NOT* a fast-forward update.
remote: *** !!! WARNING: You may have removed some important commits.
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/topic/new-feature] Change a, and create b.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/topic/new-feature
remote: X-Git-Oldrev: a60540361d47901d3fe254271779f380d94645f7
remote: X-Git-Newrev: 14d1fa28493dd548753d11729a117dadaa9905fe
remote:
remote: commit 14d1fa28493dd548753d11729a117dadaa9905fe
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri May 11 17:18:24 2012 -0700
remote:
remote:     Change a, and create b.
remote:
remote: Diff:
remote: ---
remote:  a |    2 +-
remote:  b |    1 +
remote:  2 files changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..19478f7 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,3 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, with more stuff.
remote:  Third line.
remote: diff --git a/b b/b
remote: new file mode 100644
remote: index 0000000..2dc7f8b
remote: --- /dev/null
remote: +++ b/b
remote: @@ -0,0 +1 @@
remote: +New file.
To ../bare/repo.git
 + a605403...14d1fa2 topic/new-feature -> topic/new-feature (forced update)
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
