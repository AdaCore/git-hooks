from support import *

class TestRun(TestCase):
    def test_delete_tag(self):
        """Delete a lightweight tag causing multiple commits to be lost.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :retired/gdb-7.2'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted tag retired/gdb-7.2
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/tags/retired/gdb-7.2
remote: X-Git-Oldrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The lightweight tag 'retired/gdb-7.2' was deleted.
remote: It previously pointed to:
remote:
remote:  dd6165c... Modify file `d' alone.
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   4f0f08f... Minor modifications.
remote:   4a325b3... 1 modified file, 1 new file.
remote:   cc8d2c2... Modify `c', delete `b'.
remote:   dd6165c... Modify file `d' alone.
remote:
remote: commit dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:57 2012 -0700
remote:
remote:     Modify file `d' alone.
remote:
remote: commit cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:06 2012 -0700
remote:
remote:     Modify `c', delete `b'.
remote:
remote: commit 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:20:05 2012 -0700
remote:
remote:     1 modified file, 1 new file.
remote:
remote: commit 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat May 5 15:23:36 2012 -0700
remote:
remote:     Minor modifications.
To ../bare/repo.git
 - [deleted]         retired/gdb-7.2
"""
        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
