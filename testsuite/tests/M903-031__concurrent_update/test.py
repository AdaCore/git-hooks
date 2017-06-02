from support import *
import fcntl
import os
import socket

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Simulate a push happening while another user is pushing
        # to the same repository, but using a bit of internal knowledge
        # to create a lock on the repository.

        lock_filename = os.path.join(TEST_DIR, 'bare', 'repo.git',
                                     'git-hooks::update.token.lock')
        f = open(lock_filename, 'w')
        f.write('locked by testsuite at <now> (pid = %d)'
                % os.getpid())
        f.close()

        p = Run('git push origin master'.split())
        expected_out = """\
remote: ---------------------------------------------------------------------
remote: --  Another user is currently pushing changes to this repository.  --
remote: --  Please try again in another minute or two.                     --
remote: ---------------------------------------------------------------------
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try it again, to make sure that the previous attempt did not
        # accidently deleted the lock file.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: ---------------------------------------------------------------------
remote: --  Another user is currently pushing changes to this repository.  --
remote: --  Please try again in another minute or two.                     --
remote: ---------------------------------------------------------------------
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Now, pretend that the concurrent push has finished by
        # removing our artificial lock, and verify that the push
        # now succeeds.

        os.unlink(lock_filename)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
