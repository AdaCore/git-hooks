from support import *

class TestRun(TestCase):
    def test_push_too_many_new_commits_on_master(self):
        """Try pushing too many new commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The remote should
        # reject it saying that there are too many new commits.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** This update introduces too many new commits (4), which would
remote: *** trigger as many emails, exceeding the current limit (3).
remote: *** Contact your repository adminstrator if you really meant
remote: *** to generate this many commit emails.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        self.assertRunOutputEqual(p, expected_out)

        # Now, try pushing only HEAD~, which should only push
        # 3 new commits, which should be under the limit, and
        # thus be accepted.
        p = Run('git push origin master~:master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
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
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Remove second line.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: a60540361d47901d3fe254271779f380d94645f7
remote: X-Git-Newrev: 2f3fa950307558340d5f50f825a92e73c35f64aa
remote:
remote: commit 2f3fa950307558340d5f50f825a92e73c35f64aa
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 10 09:38:01 2012 +0400
remote:
remote:     Remove second line.
remote:
remote: Diff:
remote: ---
remote:  a | 1 -
remote:  1 file changed, 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index a90d851..abde72a 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,5 +1,4 @@
remote:  Some file.
remote: -Second line, in the middle.
remote:  In the middle too!
remote:  Third line.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Re-edit a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 2f3fa950307558340d5f50f825a92e73c35f64aa
remote: X-Git-Newrev: c32bed0e676d14129183f2849470b2dfdc48e4a6
remote:
remote: commit c32bed0e676d14129183f2849470b2dfdc48e4a6
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 10 09:38:15 2012 +0400
remote:
remote:     Re-edit a.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index abde72a..55f7ecc 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,4 +1,5 @@
remote:  Some file.
remote: +Some file 2.
remote:  In the middle too!
remote:  Third line.
To ../bare/repo.git
   d065089..c32bed0  master~ -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Now, try push master again.  We should have one last
        # new commit left to push...
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Delete trailing empty line.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: c32bed0e676d14129183f2849470b2dfdc48e4a6
remote: X-Git-Newrev: 4ca9852283b70f9cf6698e8be82fd25746f1f477
remote:
remote: commit 4ca9852283b70f9cf6698e8be82fd25746f1f477
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 10 09:40:32 2012 +0400
remote:
remote:     Delete trailing empty line.
remote:
remote: Diff:
remote: ---
remote:  a | 1 -
remote:  1 file changed, 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 55f7ecc..a478316 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -2,4 +2,3 @@ Some file.
remote:  Some file 2.
remote:  In the middle too!
remote:  Third line.
remote: -
To ../bare/repo.git
   c32bed0..4ca9852  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
