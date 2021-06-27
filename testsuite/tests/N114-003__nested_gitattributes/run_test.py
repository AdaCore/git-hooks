from support import *


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing master.

        2 new commits:
            - One creating a .gitattributes;
            - One pushing some changes in tests, with a couple of files
              modified. Only one of them should be checked via cvs_check.
        """
        cd("%s/repo" % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** cvs_check: `repo' < `testsuite/tests/.gitattributes'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Do not perform precommit checks on test.py files in
remote:  testsuite/tests.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: cf7aa60ca98b115fbc691d67f6f6b10810224d29
remote: X-Git-Newrev: f2e95c7d99c45ac81569b6eaeec9f03035191060
remote:
remote: commit f2e95c7d99c45ac81569b6eaeec9f03035191060
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jan 17 08:01:07 2014 +0400
remote:
remote:     Do not perform precommit checks on test.py files in testsuite/tests.
remote:
remote: Diff:
remote: ---
remote:  testsuite/tests/.gitattributes | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/testsuite/tests/.gitattributes b/testsuite/tests/.gitattributes
remote: new file mode 100644
remote: index 0000000..25ac040
remote: --- /dev/null
remote: +++ b/testsuite/tests/.gitattributes
remote: @@ -0,0 +1 @@
remote: +*/test.py       no-precommit-check
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add comment in test_001/test.py, create test_001/test.out.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: f2e95c7d99c45ac81569b6eaeec9f03035191060
remote: X-Git-Newrev: 83afb60ef63e1d2e3c418f027e61a448bb4f589c
remote:
remote: commit 83afb60ef63e1d2e3c418f027e61a448bb4f589c
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jan 17 08:02:07 2014 +0400
remote:
remote:     Add comment in test_001/test.py, create test_001/test.out.
remote:
remote: Diff:
remote: ---
remote:  testsuite/tests/test_001/test.py | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/testsuite/tests/test_001/test.py b/testsuite/tests/test_001/test.py
remote: index cd2db80..775e4cf 100644
remote: --- a/testsuite/tests/test_001/test.py
remote: +++ b/testsuite/tests/test_001/test.py
remote: @@ -1 +1,2 @@
remote:  # An empty test.
remote: +# Explain why it is empty.
To ../bare/repo.git
   cf7aa60..83afb60  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
