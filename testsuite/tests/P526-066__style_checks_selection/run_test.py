from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one commit on master.

        The purpose is to verify that the style checker gets called
        on the correct set of files.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `gprbuild_utils.py' `tests/ada_project_path/test.py'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] An extremely important improvement over the previous version.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 22aa0fb503f1136c2e86149afec5ff2329a9e4f0
remote: X-Git-Newrev: f4b09796ba5de1698a01341bfee2897cd1d32ab0
remote:
remote: commit f4b09796ba5de1698a01341bfee2897cd1d32ab0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri May 27 08:12:43 2016 -0400
remote:
remote:     An extremely important improvement over the previous version.
remote:
remote: Diff:
remote: ---
remote:  README                          | 1 +
remote:  gprbuild_utils.py               | 1 +
remote:  support/gnat.xml                | 1 +
remote:  tests/ada_project_path/test.opt | 1 +
remote:  tests/ada_project_path/test.py  | 2 ++
remote:  5 files changed, 6 insertions(+)
remote:
remote: diff --git a/README b/README
remote: index e69de29..9bfa2ac 100644
remote: --- a/README
remote: +++ b/README
remote: @@ -0,0 +1 @@
remote: +This is the testsuite of our great tool.
remote: diff --git a/gprbuild_utils.py b/gprbuild_utils.py
remote: index e69de29..0045f7b 100644
remote: --- a/gprbuild_utils.py
remote: +++ b/gprbuild_utils.py
remote: @@ -0,0 +1 @@
remote: +\"\"\"Great Python script."
remote: diff --git a/support/gnat.xml b/support/gnat.xml
remote: index e69de29..066a446 100644
remote: --- a/support/gnat.xml
remote: +++ b/support/gnat.xml
remote: @@ -0,0 +1 @@
remote: +<--! Some XML file -->
remote: diff --git a/tests/ada_project_path/test.opt b/tests/ada_project_path/test.opt
remote: index e69de29..1aebd34 100644
remote: --- a/tests/ada_project_path/test.opt
remote: +++ b/tests/ada_project_path/test.opt
remote: @@ -0,0 +1 @@
remote: +-- This is a great test.
remote: diff --git a/tests/ada_project_path/test.py b/tests/ada_project_path/test.py
remote: index e69de29..7154281 100644
remote: --- a/tests/ada_project_path/test.py
remote: +++ b/tests/ada_project_path/test.py
remote: @@ -0,0 +1,2 @@
remote: +# Do this, and do that, and that way, we verify that our test is super
remote: +# duper.
To ../bare/repo.git
   22aa0fb..f4b0979  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
