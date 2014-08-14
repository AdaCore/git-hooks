from support import *

class TestRun(TestCase):
    def test_push_branch_with_merge_commit(self):
        """Try pushing an update to master adding one merge commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable some logging, in order to be able to see which
        # commits get checked, and what commits are being used
        # as their reference.
        self.set_debug_level(1)

        # Push master to the `origin' remote. This brings in two commits:
        #
        #   - One commit from the 'topic' branch which modifies foo.c.
        #   - The merge commit itself.
        #
        # The pre-commit check should:
        #   - Check the commit from the 'topic' branch, which means
        #     style-checking 'foo.c';
        #   - Check the merge commit, this time against the old 'master',
        #     which means style-checking 'foo.c' instead.
        #
        # The difficulty for the git-hooks comes from the fact that,
        # from the time the 'topic' branch was created, the 'README'
        # file was updated. If the git-hooks were to use the wrong
        # commit as the reference for the commit from the 'topic'
        # branch, the hooks would then be style-checking the 'README'
        # file even though it has NOT changed!

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 128c4380beb275f9002a42e0b5da3618e00c11a9, 7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: DEBUG: update base: 128c4380beb275f9002a42e0b5da3618e00c11a9
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=007bd39b476d596fbc140227f31a73247272d281, new_rev=1091f4333e5842fe4e17bd6b445f5899f13cc7e9)
remote: *** cvs_check: trunk/repo/foo.c
remote: DEBUG: check_commit(old_rev=128c4380beb275f9002a42e0b5da3618e00c11a9, new_rev=7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: *** cvs_check: trunk/repo/foo.c
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=128c4380beb275f9002a42e0b5da3618e00c11a9
remote:                         new_rev=7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: DEBUG: update base: 128c4380beb275f9002a42e0b5da3618e00c11a9
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Implement foo.c:second.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 007bd39b476d596fbc140227f31a73247272d281
remote: X-Git-Newrev: 1091f4333e5842fe4e17bd6b445f5899f13cc7e9
remote:
remote: commit 1091f4333e5842fe4e17bd6b445f5899f13cc7e9
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Jun 6 19:09:42 2013 +0400
remote:
remote:     Implement foo.c:second.
remote:
remote: Diff:
remote: ---
remote:  foo.c | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/foo.c b/foo.c
remote: index 3c82751..3665ea6 100644
remote: --- a/foo.c
remote: +++ b/foo.c
remote: @@ -5,4 +5,5 @@ foo (void)
remote:
remote:  int second (void)
remote:  {
remote: +  return 1;
remote:  }
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Merge change from the 'topic' branch.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 128c4380beb275f9002a42e0b5da3618e00c11a9
remote: X-Git-Newrev: 7277e89f8909d7279357489ccf0de81c7c0f3286
remote:
remote: commit 7277e89f8909d7279357489ccf0de81c7c0f3286
remote: Merge: 128c438 1091f43
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Jun 6 19:10:02 2013 +0400
remote:
remote:     Merge change from the 'topic' branch.
remote:
remote: Diff:
remote:
remote:  foo.c | 1 +
remote:  1 file changed, 1 insertion(+)
To ../bare/repo.git
   128c438..7277e89  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
