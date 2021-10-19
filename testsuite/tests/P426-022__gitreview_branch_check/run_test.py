def test_push_forgot(testcase):
    """Try pushing the branch named "forgot" """
    # "forgot" is a new branch. In the root directory of that
    # branch, there is a file named .gitreview, whose default
    # branch is still "master". Make sure the git-hooks reject
    # that branch creation.
    p = testcase.run("git push origin forgot".split())
    expected_out = """\
remote: *** Incorrect gerrit default branch name in file `.gitreview'.
remote: *** You probably forgot to update your .gitreview file following
remote: *** the creation of this branch.
remote: ***
remote: *** Please create a commit which updates the value
remote: *** of gerrit.defaultbranch in the file `.gitreview'
remote: *** and set it to `forgot' (instead of `master').
remote: error: hook declined to update refs/heads/forgot
To ../bare/repo.git
 ! [remote rejected] forgot -> forgot (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)


def test_push_fixed(testcase):
    """Try pushing the branch named "fixed" """
    # "fixed" is a new branch. In the root directory of that
    # branch, there is a file named .gitreview, whose default
    # branch is now set to "fixed". So this branch creation
    # should be accepted.
    p = testcase.run("git push origin fixed".split())
    expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'fixed'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/fixed
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 8a43f9e571a7ea7422ed0cc4b092700b64eab517
remote:
remote: The branch 'fixed' was created pointing to:
remote:
remote:  8a43f9e... fix defaultbranch name in .gitreview
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/fixed] Update a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/fixed
remote: X-Git-Oldrev: 16d76a092abc9e4a314e5da67d3111f3bb11a56a
remote: X-Git-Newrev: 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote:
remote: commit 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jul 28 14:32:32 2017 -0700
remote:
remote:     Update a.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index bf84ca6..22715c0 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1 +1,2 @@
remote:  Some file.
remote: +----------
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/fixed] fix defaultbranch name in .gitreview
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/fixed
remote: X-Git-Oldrev: 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote: X-Git-Newrev: 8a43f9e571a7ea7422ed0cc4b092700b64eab517
remote:
remote: commit 8a43f9e571a7ea7422ed0cc4b092700b64eab517
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jul 28 14:33:28 2017 -0700
remote:
remote:     fix defaultbranch name in .gitreview
remote:
remote: Diff:
remote: ---
remote:  .gitreview | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/.gitreview b/.gitreview
remote: index 6315846..7939b34 100644
remote: --- a/.gitreview
remote: +++ b/.gitreview
remote: @@ -2,6 +2,6 @@
remote:  host = git.adacore.com
remote:  port = 29418
remote:  project = gdb-testsuite
remote: -defaultbranch = master
remote: +defaultbranch = fixed
remote:  defaultremote = origin
To ../bare/repo.git
 * [new branch]      fixed -> fixed
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
