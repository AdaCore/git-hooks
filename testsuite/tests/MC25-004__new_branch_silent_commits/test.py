from support import *

class TestRun(TestCase):
    def test_push_head(self):
        """Try pushing new branch on remote.

        The purpose of this test is to check what happens when pushing
        a NEW branch which brings a few new commits, while at the same
        time sharing some commits from a branch marked as "no-emails".
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin head'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `.gitignore'
remote: *** cvs_check: `repo' < `source.c'
remote: *** cvs_check: `repo' < `use_source.c'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'head'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/head
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 53ec7dc719ba973a33490a696250b2bdeb931e7b
remote:
remote: The branch 'head' was created pointing to:
remote:
remote:  53ec7dc... Add file use_source.c.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   53ec7dc... Add file use_source.c.
remote:   07e4909... Resync with fsf-master as of now.
remote:   c877d1a... New file: source.c. (*)
remote:   a878a56... Add .gitignore file.
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/head] Add .gitignore file.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/head
remote: X-Git-Oldrev: c524e6e114e8e4256e54953bedcf047b08d55a60
remote: X-Git-Newrev: a878a5637be2c5ccf3186729825d96d2c9d50a7b
remote:
remote: commit a878a5637be2c5ccf3186729825d96d2c9d50a7b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 25 11:05:54 2013 +0400
remote:
remote:     Add .gitignore file.
remote:
remote: Diff:
remote: ---
remote:  .gitignore | 2 ++
remote:  1 file changed, 2 insertions(+)
remote:
remote: diff --git a/.gitignore b/.gitignore
remote: new file mode 100644
remote: index 0000000..0c7a17a
remote: --- /dev/null
remote: +++ b/.gitignore
remote: @@ -0,0 +1,2 @@
remote: +# Backup files.
remote: +*~
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/head] Resync with fsf-master as of now.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/head
remote: X-Git-Oldrev: a878a5637be2c5ccf3186729825d96d2c9d50a7b
remote: X-Git-Newrev: 07e4909783876d0b2372da64eab2996c2460f67d
remote:
remote: commit 07e4909783876d0b2372da64eab2996c2460f67d
remote: Merge: a878a56 c877d1a
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 25 11:08:53 2013 +0400
remote:
remote:     Resync with fsf-master as of now.
remote:
remote:     There is a change that we need in order to implement the new feature
remote:     that will bring this program to another level.
remote:
remote: Diff:
remote:
remote:  source.c | 1 +
remote:  1 file changed, 1 insertion(+)
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/head] Add file use_source.c.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/head
remote: X-Git-Oldrev: 07e4909783876d0b2372da64eab2996c2460f67d
remote: X-Git-Newrev: 53ec7dc719ba973a33490a696250b2bdeb931e7b
remote:
remote: commit 53ec7dc719ba973a33490a696250b2bdeb931e7b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 25 11:11:03 2013 +0400
remote:
remote:     Add file use_source.c.
remote:
remote: Diff:
remote: ---
remote:  use_source.c | 3 +++
remote:  1 file changed, 3 insertions(+)
remote:
remote: diff --git a/use_source.c b/use_source.c
remote: new file mode 100644
remote: index 0000000..9436798
remote: --- /dev/null
remote: +++ b/use_source.c
remote: @@ -0,0 +1,3 @@
remote: +extern void do_nothing (void);
remote: +
remote: +void do_something (void) { do_nothing ();}
To ../bare/repo.git
 * [new branch]      head -> head
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s head'.split())
        expected_out = """\
53ec7dc719ba973a33490a696250b2bdeb931e7b
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
