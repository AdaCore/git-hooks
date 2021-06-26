from support import *


class TestRun(TestCase):
    def test_pushes(testcase):
        """Test various pushes to multi-project repository.
        """
        cd('%s/repo' % TEST_DIR)

        # First, adjust the project.config file to use a script to
        # compute the email recipients.  We have to do it manually
        # here, because we need to provide the full path to that
        # script, which isn't known until now.
        with open('%s/hooks_config' % TEST_DIR) as f:
            project_config = f.read() % {'TEST_DIR': TEST_DIR}
        with open('project.config', 'w') as f:
            f.write(project_config)
        p = Run(['git', 'commit', '-m', 'fix hooks.mailinglist',
                 'project.config'])
        assert p.status == 0, p.image

        p = Run(['git', 'push', 'origin',
                 'refs/heads/meta/config:refs/meta/config'])
        assert p.status == 0, p.image

        p = Run('git checkout master'.split())
        assert p.status == 0, p.image

        # Push the first commit. This is a binutils commit, so
        # should be sent to the binutils ml only.
        p = Run(['git', 'push', 'origin',
                 '4207b94cadc3c1be0edb4f6df5670f0311c267f3:master'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] A binutils change.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: ab5227e384f96e2914ddf197bc5f826e8f979e19
remote: X-Git-Newrev: 4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote:
remote: commit 4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:00:58 2014 -0500
remote:
remote:     A binutils change.
remote:
remote:     This change introduces struct bfd.
remote:
remote: Diff:
remote: ---
remote:  bfd/bfd-in.h | 5 +++++
remote:  1 file changed, 5 insertions(+)
remote:
remote: diff --git a/bfd/bfd-in.h b/bfd/bfd-in.h
remote: index e0b0f02..14bc0a5 100644
remote: --- a/bfd/bfd-in.h
remote: +++ b/bfd/bfd-in.h
remote: @@ -1 +1,6 @@
remote:  /* Some BFD code.  */
remote: +
remote: +struct bfd
remote: +{
remote: +  int handle;
remote: +};
To ../bare/repo.git
   ab5227e..4207b94  4207b94cadc3c1be0edb4f6df5670f0311c267f3 -> master
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push the next commit, which is a GDB commit and thus should
        # be sent to the gdb ml only.
        p = Run(['git', 'push', 'origin',
                 'cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d:master'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add start_mainloop declaration in top.h.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote: X-Git-Newrev: cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote:
remote: commit cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:02:04 2014 -0500
remote:
remote:     Add start_mainloop declaration in top.h.
remote:
remote: Diff:
remote: ---
remote:  gdb/top.h | 2 ++
remote:  1 file changed, 2 insertions(+)
remote:
remote: diff --git a/gdb/top.h b/gdb/top.h
remote: index 4c60c8f..d969b4d 100644
remote: --- a/gdb/top.h
remote: +++ b/gdb/top.h
remote: @@ -1 +1,3 @@
remote:  /* top.h */
remote: +
remote: +extern void start_mainloop (void);
To ../bare/repo.git
   4207b94..cd2f5d4  cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d -> master
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push the next commit, which is a commit touching both
        # a binutile file and GDB file, and so should be emailed
        # to both projects.
        p = Run(['git', 'push', 'origin',
                 '4c7588eee23d6d42e8d50ba05343e3d0f31dd286:master'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add filename in struct bfd, and add README in GDB.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote: X-Git-Newrev: 4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote:
remote: commit 4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:03:36 2014 -0500
remote:
remote:     Add filename in struct bfd, and add README in GDB.
remote:
remote:     This is just to create a commit that combines changes in both binutils
remote:     and GDB.
remote:
remote: Diff:
remote: ---
remote:  bfd/bfd-in.h | 1 +
remote:  gdb/README   | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/bfd/bfd-in.h b/bfd/bfd-in.h
remote: index 14bc0a5..94b4f5b 100644
remote: --- a/bfd/bfd-in.h
remote: +++ b/bfd/bfd-in.h
remote: @@ -3,4 +3,5 @@
remote:  struct bfd
remote:  {
remote:    int handle;
remote: +  char *filename;
remote:  };
remote: diff --git a/gdb/README b/gdb/README
remote: new file mode 100644
remote: index 0000000..3574541
remote: --- /dev/null
remote: +++ b/gdb/README
remote: @@ -0,0 +1 @@
remote: +Note that GDB depends on BFD.
To ../bare/repo.git
   cd2f5d4..4c7588e  4c7588eee23d6d42e8d50ba05343e3d0f31dd286 -> master
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push the next commit, which is a commit touching a file
        # which is common to both binutils and GDB.
        p = Run(['git', 'push', 'origin',
                 '0ed035c4417a51987594586016b061bed362ec9b:master'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Call AC_INIT in configure.ac
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote: X-Git-Newrev: 0ed035c4417a51987594586016b061bed362ec9b
remote:
remote: commit 0ed035c4417a51987594586016b061bed362ec9b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:05:03 2014 -0500
remote:
remote:     Call AC_INIT in configure.ac
remote:
remote: Diff:
remote: ---
remote:  configure.ac | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/configure.ac b/configure.ac
remote: index 926bea2..e90f03e 100644
remote: --- a/configure.ac
remote: +++ b/configure.ac
remote: @@ -1 +1 @@
remote: -# Nothing there yet.
remote: +AC_INIT(bfd/bfd-in.h)
To ../bare/repo.git
   4c7588e..0ed035c  0ed035c4417a51987594586016b061bed362ec9b -> master
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push the final commit, which is a merge commit with one
        # pre-existing commit.
        p = Run(['git', 'push', 'origin', 'master'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Subject: [repo] (2 commits) Merge new feature from branch contrib/new-feature.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 0ed035c4417a51987594586016b061bed362ec9b
remote: X-Git-Newrev: 5884482fa14bb5ae552cd601f78d6b5de6ed1c40
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  5884482... Merge new feature from branch contrib/new-feature.
remote:
remote: It previously pointed to:
remote:
remote:  0ed035c... Call AC_INIT in configure.ac
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   5884482... Merge new feature from branch contrib/new-feature.
remote:   1ef49af... Implement new GDB feature. (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Merge new feature from branch contrib/new-feature.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 0ed035c4417a51987594586016b061bed362ec9b
remote: X-Git-Newrev: 5884482fa14bb5ae552cd601f78d6b5de6ed1c40
remote:
remote: commit 5884482fa14bb5ae552cd601f78d6b5de6ed1c40
remote: Merge: 0ed035c 1ef49af
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Dec 14 09:06:50 2014 -0500
remote:
remote:     Merge new feature from branch contrib/new-feature.
remote:
remote: Diff:
remote: ---
remote:  gdb/feature.c | 1 +
remote:  1 file changed, 1 insertion(+)
To ../bare/repo.git
   0ed035c..5884482  master -> master
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push a tag to a bfd commit.
        p = Run(['git', 'push', 'origin', 'bfd-tag'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Created tag 'bfd-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/bfd-tag
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 035e5c30aab982043b33eff5411c3d2bf83e2eaf
remote:
remote: The unsigned tag 'bfd-tag' was created pointing to:
remote:
remote:  4207b94... A binutils change.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Sat Dec 13 19:35:45 2014 -0500
remote:
remote:     A binutils change...
To ../bare/repo.git
 * [new tag]         bfd-tag -> bfd-tag
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push a tag to a GDB commit.
        p = Run(['git', 'push', 'origin', 'gdb-tag'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Subject: [repo] Created tag 'gdb-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/gdb-tag
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 5884482fa14bb5ae552cd601f78d6b5de6ed1c40
remote:
remote: The lightweight tag 'gdb-tag' was created pointing to:
remote:
remote:  5884482... Merge new feature from branch contrib/new-feature.
To ../bare/repo.git
 * [new tag]         gdb-tag -> gdb-tag
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push a tag to a common commit.
        p = Run(['git', 'push', 'origin', 'common-tag'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Subject: [repo] Created tag 'common-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/common-tag
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 0ed035c4417a51987594586016b061bed362ec9b
remote:
remote: The lightweight tag 'common-tag' was created pointing to:
remote:
remote:  0ed035c... Call AC_INIT in configure.ac
To ../bare/repo.git
 * [new tag]         common-tag -> common-tag
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Push all git notes.
        p = Run(['git', 'push', 'origin',
                 'refs/notes/commits:refs/notes/commits'])
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] A binutils change.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev:
remote: X-Git-Newrev: f92c5af7ed4374d7174b8e7c25cd89cea5c1b6c3
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     A bfd note.
remote:
remote: This note annotates the following commit:
remote:
remote: commit 4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:00:58 2014 -0500
remote:
remote:     A binutils change.
remote:
remote:     This change introduces struct bfd.
remote:
remote: Diff:
remote:
remote: diff --git a/4207b94cadc3c1be0edb4f6df5670f0311c267f3 b/4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote: new file mode 100644
remote: index 0000000..70b6f6e
remote: --- /dev/null
remote: +++ b/4207b94cadc3c1be0edb4f6df5670f0311c267f3
remote: @@ -0,0 +1 @@
remote: +A bfd note.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] Add start_mainloop declaration in top.h.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: f92c5af7ed4374d7174b8e7c25cd89cea5c1b6c3
remote: X-Git-Newrev: dc30675096eb6cc1fc91f14286582387dd0d5183
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     A short GDB note.
remote:
remote: This note annotates the following commit:
remote:
remote: commit cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:02:04 2014 -0500
remote:
remote:     Add start_mainloop declaration in top.h.
remote:
remote: Diff:
remote:
remote: diff --git a/cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d b/cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote: new file mode 100644
remote: index 0000000..273aed2
remote: --- /dev/null
remote: +++ b/cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d
remote: @@ -0,0 +1 @@
remote: +A short GDB note.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: bfd-cvs@example.com, gdb-cvs@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] Add filename in struct bfd, and add README in GDB.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: dc30675096eb6cc1fc91f14286582387dd0d5183
remote: X-Git-Newrev: 83820cec54feb2b77847ddab68534eeed84c2d0d
remote:
remote: A Git note has been updated; it now contains:
remote:
remote:     Synchronized change between binutils and GDB.
remote:
remote: This note annotates the following commit:
remote:
remote: commit 4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 13 19:03:36 2014 -0500
remote:
remote:     Add filename in struct bfd, and add README in GDB.
remote:
remote:     This is just to create a commit that combines changes in both binutils
remote:     and GDB.
remote:
remote: Diff:
remote:
remote: diff --git a/4c7588eee23d6d42e8d50ba05343e3d0f31dd286 b/4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote: new file mode 100644
remote: index 0000000..137e41c
remote: --- /dev/null
remote: +++ b/4c7588eee23d6d42e8d50ba05343e3d0f31dd286
remote: @@ -0,0 +1 @@
remote: +Synchronized change between binutils and GDB.
To ../bare/repo.git
 * [new branch]      refs/notes/commits -> refs/notes/commits
"""
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
