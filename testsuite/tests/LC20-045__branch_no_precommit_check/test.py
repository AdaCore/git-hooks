from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # We want to force the "in hooks.no-precommit-check" debug trace...
        self.set_debug_level(1)

        # There should be no pre-commit checks on branch master.
        # This is verified two ways:
        #   - There are no cvs_check debug traces in the output;
        #   - The cvs_check script has been setup to reject everything;
        #     so if it gets called, the update will be rejected.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 9cbe95153dd093ef72c0dcb27094c9c6cdd97ad9, e7007066aeb5fefeba7d226e5a31c70971b67cdb)
remote: DEBUG: update base: 9cbe95153dd093ef72c0dcb27094c9c6cdd97ad9
remote: DEBUG: (hooks.no-precommit-check match: `refs/heads/master')
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=9cbe95153dd093ef72c0dcb27094c9c6cdd97ad9
remote:                         new_rev=e7007066aeb5fefeba7d226e5a31c70971b67cdb)
remote: DEBUG: update base: 9cbe95153dd093ef72c0dcb27094c9c6cdd97ad9
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Update all files.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 9cbe95153dd093ef72c0dcb27094c9c6cdd97ad9
remote: X-Git-Newrev: e7007066aeb5fefeba7d226e5a31c70971b67cdb
remote:
remote: commit e7007066aeb5fefeba7d226e5a31c70971b67cdb
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Jun 10 17:17:03 2012 -0700
remote:
remote:     Update all files.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  b | 2 ++
remote:  c | 1 +
remote:  3 files changed, 4 insertions(+)
remote:
remote: diff --git a/a b/a
remote: index 73af989..1b25a6e 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,3 @@
remote:  First file.
remote: +-----------
remote:  Some contents.
remote: diff --git a/b b/b
remote: index 8dae410..8b7fc7b 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,3 +1,5 @@
remote:  Second file.
remote:  Some other contents.
remote:  A third line.
remote: +-- A Style violation on the next line, but we've decided it's OK.
remote: +Trailing Space at end of line.
remote: diff --git a/c b/c
remote: index da60479..8ffbf8d 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,4 +1,5 @@
remote:  Final file.
remote: +-----------
remote:  Yet more contents.
remote:
remote:  A line after some empty line.
To ../bare/repo.git
   9cbe951..e700706  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
