from support import *
import os


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master."""
        # Create an adapted version of the environment we can then
        # pass when calling Git for the purpose of this testcase.
        env = os.environ.copy()

        # We are trying to test the use of the hooks.style-checker config
        # option, which means we need to unset GIT_HOOKS_STYLE_CHECKER.
        # Otherwise, the latter overrides the operational behavior
        # which we are trying to test.
        del env["GIT_HOOKS_STYLE_CHECKER"]

        # The hooks.style-checker option only contains the name
        # of the program to call, but not the full path to that
        # program. Update the PATH so that the git-hooks find it.
        env["PATH"] = testcase.work_dir + ":" + env["PATH"]

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin master".split(), env=env, ignore_environ=True)
        expected_out = """\
remote: *** alt_style_checker: `repo' < `a'
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
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()