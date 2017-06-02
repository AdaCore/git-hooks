from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = r"""
remote: *** cvs_check: `repo' < `"full-double"'
remote: *** cvs_check: `repo' < `'full-single''
remote: *** cvs_check: `repo' < ``backtick`'
remote: *** cvs_check: `repo' < `bad\dir/"two"'
remote: *** cvs_check: `repo' < `bad\dir/'one''
remote: *** cvs_check: `repo' < `bad\dir/`lish'
remote: *** cvs_check: `repo' < `bad\dir/nasa esa'
remote: *** cvs_check: `repo' < `bad\dir/normal_filename'
remote: *** cvs_check: `repo' < `bad\dir/one'two"3'
remote: *** cvs_check: `repo' < `bad\dir/pet`ular'
remote: *** cvs_check: `repo' < `front`tick'
remote: *** cvs_check: `repo' < `one space'
remote: *** cvs_check: `repo' < `subdir/"double"'
remote: *** cvs_check: `repo' < `subdir/'single''
remote: *** cvs_check: `repo' < `subdir/another\bs.txt'
remote: *** cvs_check: `repo' < `subdir/automa`'
remote: *** cvs_check: `repo' < `subdir/hello:world'
remote: *** cvs_check: `repo' < `subdir/sp ace'
remote: *** cvs_check: `repo' < `subdir/time`tock'
remote: *** cvs_check: `repo' < `weird:colon.h'
remote: *** cvs_check: `repo' < `weird\backslash.c'
remote: *** cvs_check: `repo' < `with"double-quote'
remote: *** cvs_check: `repo' < `with'single-quote'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Add some files and dirs with unusual names.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 123f5e1a422c5c5d0dbb15c8f65e63cea1f23a04
remote:
remote: commit 123f5e1a422c5c5d0dbb15c8f65e63cea1f23a04
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Feb 24 16:30:49 2017 +0400
remote:
remote:     Add some files and dirs with unusual names.
remote:
remote: Diff:
remote: ---
remote:  "\"full-double\""          | 0
remote:  'full-single'              | 0
remote:  `backtick`                 | 0
remote:  "bad\\dir/\"two\""         | 0
remote:  "bad\\dir/'one'"           | 0
remote:  "bad\\dir/`lish"           | 0
remote:  "bad\\dir/nasa esa"        | 0
remote:  "bad\\dir/normal_filename" | 0
remote:  "bad\\dir/one'two\"3"      | 0
remote:  "bad\\dir/pet`ular"        | 0
remote:  front`tick                 | 0
remote:  one space                  | 0
remote:  "subdir/\"double\""        | 0
remote:  subdir/'single'            | 0
remote:  "subdir/another\\bs.txt"   | 1 +
remote:  subdir/automa`             | 0
remote:  subdir/hello:world         | 0
remote:  subdir/sp ace              | 0
remote:  subdir/time`tock           | 0
remote:  weird:colon.h              | 1 +
remote:  "weird\\backslash.c"       | 1 +
remote:  "with\"double-quote"       | 0
remote:  with'single-quote          | 0
remote:  23 files changed, 3 insertions(+)
remote:
remote: diff --git "a/\"full-double\"" "b/\"full-double\""
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/'full-single' b/'full-single'
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/`backtick` b/`backtick`
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/\"two\"" "b/bad\\dir/\"two\""
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/'one'" "b/bad\\dir/'one'"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/`lish" "b/bad\\dir/`lish"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/nasa esa" "b/bad\\dir/nasa esa"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/normal_filename" "b/bad\\dir/normal_filename"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/one'two\"3" "b/bad\\dir/one'two\"3"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/bad\\dir/pet`ular" "b/bad\\dir/pet`ular"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/front`tick b/front`tick
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/one space b/one space
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/subdir/\"double\"" "b/subdir/\"double\""
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/subdir/'single' b/subdir/'single'
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git "a/subdir/another\\bs.txt" "b/subdir/another\\bs.txt"
remote: new file mode 100644
remote: index 0000000..9448ff6
remote: --- /dev/null
remote: +++ "b/subdir/another\\bs.txt"
remote: @@ -0,0 +1 @@
remote: +Another file with a weird name.
remote: diff --git a/subdir/automa` b/subdir/automa`
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/subdir/hello:world b/subdir/hello:world
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/subdir/sp ace b/subdir/sp ace
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/subdir/time`tock b/subdir/time`tock
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/weird:colon.h b/weird:colon.h
remote: new file mode 100644
remote: index 0000000..3db3497
remote: --- /dev/null
remote: +++ b/weird:colon.h
remote: @@ -0,0 +1 @@
remote: +A file with a colon in its name.
remote: diff --git "a/weird\\backslash.c" "b/weird\\backslash.c"
remote: new file mode 100644
remote: index 0000000..76e0a4e
remote: --- /dev/null
remote: +++ "b/weird\\backslash.c"
remote: @@ -0,0 +1 @@
remote: +First weird file (with a backslash in it).
remote: diff --git "a/with\"double-quote" "b/with\"double-quote"
remote: new file mode 100644
remote: index 0000000..e69de29
remote: diff --git a/with'single-quote b/with'single-quote
remote: new file mode 100644
remote: index 0000000..e69de29
To ../bare/repo.git
   d065089..123f5e1  master -> master
"""[1:]  # To strip the extra newline at the start introduce for visuals only

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
