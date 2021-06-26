from support import *

class TestRun(TestCase):
    def test_push_on_branch_with_email_new_commits_only(testcase):
        cd ('%s/repo' % TEST_DIR)

        # This testcase verifies the behavior of the hooks relative
        # to a branch which has the hooks.email-new-commits-only
        # option set. To do so, this testcase repository has been
        # created with:
        #
        # - A branch called `master', with the commits as shown, and
        #   already pushed to origin:
        #
        #       A  <--  B  <-- C  <-- D  <-- E <-- master
        #
        # - A branch called `feature', which simulates a branch created
        #   by a user to work on a given feature outside of the main
        #   development branch (master);
        #
        #   The hooks configuration for this repository is such that
        #   the hooks.email-new-commits-only matches this branch name.
        #
        # - A number of branches called `feature-1', `feature-2',
        #   `feature-3', etc, where each branch represents a further
        #   state of the `feature' branch after some work done by
        #   the user. Each branch has been created to simulate different
        #   scenarios, which we will explain via comments while pushing
        #   those branches.

        # Push branch `feature', which contains two commits on top of
        # commit A from master:
        #
        #       A  <-- F1 <-- F2 <-- feature
        #
        # We should see commit-emails for both F1 and F2, as usual.

        p = testcase.run('git push origin feature'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `f1'
remote: *** cvs_check: `repo' < `f2'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'feature'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: c305de8d7c17407c8d55ceca6b8fd0586d142850
remote:
remote: The branch 'feature' was created pointing to:
remote:
remote:  c305de8... Add file: f2
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f1
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: ed652ceb8ec59e7da0c0e4f5f201961b92db57d2
remote: X-Git-Newrev: 5b23095f6986518d49337243bd8ea6888acb7051
remote:
remote: commit 5b23095f6986518d49337243bd8ea6888acb7051
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:27:53 2020 -0700
remote:
remote:     Add file: f1
remote:
remote: Diff:
remote: ---
remote:  f1 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f1 b/f1
remote: new file mode 100644
remote: index 0000000..c811e21
remote: --- /dev/null
remote: +++ b/f1
remote: @@ -0,0 +1 @@
remote: +File f1
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f2
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 5b23095f6986518d49337243bd8ea6888acb7051
remote: X-Git-Newrev: c305de8d7c17407c8d55ceca6b8fd0586d142850
remote:
remote: commit c305de8d7c17407c8d55ceca6b8fd0586d142850
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:28:09 2020 -0700
remote:
remote:     Add file: f2
remote:
remote: Diff:
remote: ---
remote:  f2 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f2 b/f2
remote: new file mode 100644
remote: index 0000000..dfd370a
remote: --- /dev/null
remote: +++ b/f2
remote: @@ -0,0 +1 @@
remote: +File f2
To ../bare/repo.git
 * [new branch]      feature -> feature
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Push branch `feature-2' as `feature'.
        #
        # This branch contains the same two commits as branch `feature',
        # but rebased on top of commit C from master:
        #
        #       ... <-- C <-- F1' <-- F2' <-- feature-2
        #
        # Because this is a non-fast-forward update, we need to
        # force push (-f).

        p = testcase.run('git push -f origin feature-2:feature'.split())
        expected_out = """\
remote: *** !!! WARNING: This is *NOT* a fast-forward update.
remote: *** !!! WARNING: You may have removed some important commits.
remote: *** cvs_check: `repo' < `f1'
remote: *** cvs_check: `repo' < `f2'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo/feature] (4 commits) Add file: f2
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: c305de8d7c17407c8d55ceca6b8fd0586d142850
remote: X-Git-Newrev: 33c342b4fc9bbec74ed0f6ef8b3d31ff9534a660
remote:
remote: The branch 'feature' was updated to point to:
remote:
remote:  33c342b... Add file: f2
remote:
remote: It previously pointed to:
remote:
remote:  c305de8... Add file: f2
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   c305de8... Add file: f2
remote:   5b23095... Add file: f1
remote:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   33c342b... Add file: f2
remote:   2ffd6e3... Add file: f1
remote:   9e87ed9... Add new file: c (*)
remote:   9971219... Add new file: b (*)
remote:
remote: (*) This commit already exists in another branch.
remote:     Because the reference `refs/heads/feature' matches
remote:     your hooks.email-new-commits-only configuration,
remote:     no separate email is sent for this commit.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f1
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 9e87ed9830374c47a84e010c091ca8e4848d10c1
remote: X-Git-Newrev: 2ffd6e30fb2c832bfa34d5676a69c1fc1505043c
remote:
remote: commit 2ffd6e30fb2c832bfa34d5676a69c1fc1505043c
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:27:53 2020 -0700
remote:
remote:     Add file: f1
remote:
remote: Diff:
remote: ---
remote:  f1 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f1 b/f1
remote: new file mode 100644
remote: index 0000000..c811e21
remote: --- /dev/null
remote: +++ b/f1
remote: @@ -0,0 +1 @@
remote: +File f1
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f2
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 2ffd6e30fb2c832bfa34d5676a69c1fc1505043c
remote: X-Git-Newrev: 33c342b4fc9bbec74ed0f6ef8b3d31ff9534a660
remote:
remote: commit 33c342b4fc9bbec74ed0f6ef8b3d31ff9534a660
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:28:09 2020 -0700
remote:
remote:     Add file: f2
remote:
remote: Diff:
remote: ---
remote:  f2 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f2 b/f2
remote: new file mode 100644
remote: index 0000000..dfd370a
remote: --- /dev/null
remote: +++ b/f2
remote: @@ -0,0 +1 @@
remote: +File f2
To ../bare/repo.git
 + c305de8...33c342b feature-2 -> feature (forced update)
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Push branch `feature-3' as `feature'.
        #
        # This branch adds two new commits on top of `feature-2':
        #
        #       ... <-- F2' <-- F3 <-- F4 <-- feature-3
        #
        # So, we expect commit emails to be sent for those 2 commits.

        p = testcase.run('git push origin feature-3:feature'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `f3'
remote: *** cvs_check: `repo' < `f4'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f3
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 33c342b4fc9bbec74ed0f6ef8b3d31ff9534a660
remote: X-Git-Newrev: b9044cc060a2fc87f4f31efed6de895471db3fa8
remote:
remote: commit b9044cc060a2fc87f4f31efed6de895471db3fa8
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:30:55 2020 -0700
remote:
remote:     Add file: f3
remote:
remote: Diff:
remote: ---
remote:  f3 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f3 b/f3
remote: new file mode 100644
remote: index 0000000..55204ca
remote: --- /dev/null
remote: +++ b/f3
remote: @@ -0,0 +1 @@
remote: +File f3
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] Add file: f4
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: b9044cc060a2fc87f4f31efed6de895471db3fa8
remote: X-Git-Newrev: 4bb270f28b95750773f040ac91538e39c06a3b32
remote:
remote: commit 4bb270f28b95750773f040ac91538e39c06a3b32
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:31:10 2020 -0700
remote:
remote:     Add file: f4
remote:
remote: Diff:
remote: ---
remote:  f4 | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/f4 b/f4
remote: new file mode 100644
remote: index 0000000..8776885
remote: --- /dev/null
remote: +++ b/f4
remote: @@ -0,0 +1 @@
remote: +File f4
To ../bare/repo.git
   33c342b..4bb270f  feature-3 -> feature
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Push branch `feature-4' as `feature'.
        #
        # This branch simulates a user updating his feature branch
        # via a merge of branch master. Since `feature-3' already
        # had commits A, B and C from master, this gives us the following
        # graph for `feature-4' (knowing that `feature-3' points to F4):
        #
        #       ... <-- D <-- E <---+- F5 <-- feature-4
        #                          /
        #            ... <-- F4 <-+
        #
        # When pushing this commit, the only commit that's new for
        # this repository is commit F5, so this is the only commit
        # for which a commit-email should be sent (besides the
        # summary-of-changes email).

        p = testcase.run('git push origin feature-4:feature'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `d' `e'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo/feature] (3 commits) import latest changes from branch 'master'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 4bb270f28b95750773f040ac91538e39c06a3b32
remote: X-Git-Newrev: 785f3f1df8f5734bd3a26e594822861272cc9b02
remote:
remote: The branch 'feature' was updated to point to:
remote:
remote:  785f3f1... import latest changes from branch 'master'
remote:
remote: It previously pointed to:
remote:
remote:  4bb270f... Add file: f4
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   785f3f1... import latest changes from branch 'master'
remote:   a76ef39... Add new file: e (*)
remote:   fa88937... Add new file: d (*)
remote:
remote: (*) This commit already exists in another branch.
remote:     Because the reference `refs/heads/feature' matches
remote:     your hooks.email-new-commits-only configuration,
remote:     no separate email is sent for this commit.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/feature] import latest changes from branch 'master'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/feature
remote: X-Git-Oldrev: 4bb270f28b95750773f040ac91538e39c06a3b32
remote: X-Git-Newrev: 785f3f1df8f5734bd3a26e594822861272cc9b02
remote:
remote: commit 785f3f1df8f5734bd3a26e594822861272cc9b02
remote: Merge: 4bb270f a76ef39
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Aug 15 12:32:35 2020 -0700
remote:
remote:     import latest changes from branch 'master'
remote:
remote: Diff:
remote: ---
remote:  d | 1 +
remote:  e | 1 +
remote:  2 files changed, 2 insertions(+)
To ../bare/repo.git
   4bb270f..785f3f1  feature-4 -> feature
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Verify that the hooks.no-emails config takes precendence
        # over the hooks.email-new-commits-only config.
        #
        # For that test, push a new branch, called `feature-no-emails'.
        # which matches both config options above. We expect the update
        # to be accepted, and no email to be sent.
        p = testcase.run('git push origin feature-no-emails'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `n'
remote: *** cvs_check: `repo' < `n2'
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/.*no-emails.*',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/feature-no-emails).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
 * [new branch]      feature-no-emails -> feature-no-emails
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
