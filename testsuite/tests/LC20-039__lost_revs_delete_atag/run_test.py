from support import *

class TestRun(TestCase):
    def test_delete_tag(self):
        """Try deteting tag retired/gdb-7.2...

        ... knowing that this will cause several commits to be lost.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :retired/gdb-7.2'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted tag 'retired/gdb-7.2'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/retired/gdb-7.2
remote: X-Git-Oldrev: 0c8f5c4eb5e58eb59b9a69019581004950de581d
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The annotated tag 'retired/gdb-7.2' was deleted.
remote: It previously pointed to:
remote:
remote:  dd6165c... Modify file `d' alone.
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   dd6165c... Modify file `d' alone.
remote:   cc8d2c2... Modify `c', delete `b'.
remote:   4a325b3... 1 modified file, 1 new file.
remote:   4f0f08f... Minor modifications.
To ../bare/repo.git
 - [deleted]         retired/gdb-7.2
"""
        assert p.status == 0, p.image
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
