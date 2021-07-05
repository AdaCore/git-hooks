from support import TestCase, runtests


class TestRun(TestCase):
    def test_update_branch_custom_name_recognized(testcase):
        """Push a branch update using a custom reference name."""
        p = testcase.run("git push origin my-topic:refs/user/myself/my-feature".split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/user/myself/my-feature)] update a to add terminator line
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/user/myself/my-feature
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 2a112bb1c30346f6287bb3d5c157a93235ea861f
remote:
remote: commit 2a112bb1c30346f6287bb3d5c157a93235ea861f
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Mar 1 20:15:13 2020 +0400
remote:
remote:     update a to add terminator line
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..698778b 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,4 @@
remote:  Some file.
remote:  Second line.
remote:  Third line.
remote: +Terminator.
To ../bare/repo.git
   d065089..2a112bb  my-topic -> refs/user/myself/my-feature
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
