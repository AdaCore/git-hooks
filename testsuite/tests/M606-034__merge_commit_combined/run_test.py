def test_push_branch_with_merge_commit(testcase):
    """Try pushing an update to master adding one merge commit."""
    # Enable some logging, in order to be able to see which
    # commits get checked, and what commits are being used
    # as their reference.
    testcase.set_debug_level(1)

    # Push master to the `origin' remote. This brings in two commits:
    #
    #   - One commit from the 'topic' branch which modifies foo.c.
    #   - The merge commit itself.
    #
    # Because we are in combined-style-checking mode, there should
    # only be one commit check, of the merge commit, using the old
    # master's SHA1 as the "parent".

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 128c4380beb275f9002a42e0b5da3618e00c11a9, 7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: DEBUG: update base: 128c4380beb275f9002a42e0b5da3618e00c11a9
remote: DEBUG: (combined style checking)
remote: DEBUG: style_check_commit(old_rev=128c4380beb275f9002a42e0b5da3618e00c11a9, new_rev=7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: *** cvs_check: `repo' < `foo.c'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=128c4380beb275f9002a42e0b5da3618e00c11a9
remote:                         new_rev=7277e89f8909d7279357489ccf0de81c7c0f3286)
remote: DEBUG: update base: 128c4380beb275f9002a42e0b5da3618e00c11a9
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
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
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
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
remote: ---
remote:  foo.c | 1 +
remote:  1 file changed, 1 insertion(+)
To ../bare/repo.git
   128c438..7277e89  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
