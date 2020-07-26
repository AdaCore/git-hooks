from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, =?utf-8?b?TcOibsO8IFNjcmlwdA==?= <ms@example.com>
remote: Bcc: filer@example.com
remote: Subject: [repo] Expand contents of file A.
remote: X-Act-Checkin: repo
remote: X-Git-Author: =?utf-8?b?SsOpcsO0bWUgTsOvbcO4?= <nimo@nowhere.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 15f28e076a944b3fbe98ebb1053e60cb43bc6751
remote:
remote: commit 15f28e076a944b3fbe98ebb1053e60cb43bc6751
remote: Author: J\xc3\xa9r\xc3\xb4me N\xc3\xafm\xc3\xb8 <nimo@nowhere.com>
remote: Date:   Sun Sep 20 16:09:45 2015 -0700
remote:
remote:     Expand contents of file A.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index 78822b6..a83c600 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,3 @@
remote:  This is a file
remote:  with a second line.
remote: +And now a third line.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 8bit
remote: Content-Type: text/plain; charset="iso-8859-1"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, =?utf-8?b?TcOibsO8IFNjcmlwdA==?= <ms@example.com>
remote: Bcc: filer@example.com
remote: Subject: [repo] Remove useless comment in "b"
remote: X-Act-Checkin: repo
remote: X-Git-Author: =?iso-8859-1?q?M=E3n=FC_Script?= <script@example.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 15f28e076a944b3fbe98ebb1053e60cb43bc6751
remote: X-Git-Newrev: 98bda8f3aa783282348a39ddf816413e54847d6d
remote:
remote: commit 98bda8f3aa783282348a39ddf816413e54847d6d
remote: Author: M\xe3n\xfc Script <script@example.com>
remote: Date:   Sun Sep 20 16:17:06 2015 -0700
remote:
remote:     Remove useless comment in "b"
remote:
remote: Diff:
remote: ---
remote:  b | 1 -
remote:  1 file changed, 1 deletion(-)
remote:
remote: diff --git a/b b/b
remote: index 373ad20..d714a82 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,3 +1,2 @@
remote:  some contents inside
remote:  that file
remote: -that isn't really all that interesting.
To ../bare/repo.git
   426fba3..98bda8f  master -> master
"""
        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
