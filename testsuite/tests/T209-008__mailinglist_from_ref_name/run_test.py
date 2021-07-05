from support import *


class TestRun(TestCase):
    def test_push_commit_on_master_and_release_x(testcase):
        """Try pushing a commit on two branches."""
        # First, adjust the project.config file to use a script to
        # compute the email recipients.  We have to do it manually
        # here, because we need to provide the full path to that
        # script, which isn't known until now.

        p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
        assert p.status == 0, p.image

        p = testcase.run(["git", "checkout", "FETCH_HEAD"])
        assert p.status == 0, p.image

        with open("%s/hooks_config" % TEST_DIR) as f:
            project_config = f.read() % {"TEST_DIR": TEST_DIR}
        with open(os.path.join(testcase.repo_dir, "project.config"), "w") as f:
            f.write(project_config)
        p = testcase.run(
            ["git", "commit", "-m", "fix hooks.mailinglist", "project.config"]
        )
        assert p.status == 0, p.image

        p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
        assert p.status == 0, p.image

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified, and the hooks.mailinglist
        # script should see that it is being called for refs/heads/master,
        # and return that the mailing list to use is devel-commits@[...].

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: devel-commits@example.com
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
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Do the same as above, but this time with the 'release-x' branch.
        # This time around, the hooks.mailinglist script should detect
        # that the branch name starts with "release-", and thus return
        # a different email address.

        p = testcase.run("git push origin release-x".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: release-commits@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/release-x] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/release-x
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
   d065089..a605403  release-x -> release-x
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
