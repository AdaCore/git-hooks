from support import *


class TestRun(TestCase):
    def test_pushes(self):
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
        self.assertTrue(p.status == 0, p.image)

        p = Run(['git', 'push', 'origin',
                 'refs/heads/meta/config:refs/meta/config'])
        self.assertTrue(p.status == 0, p.image)

        p = Run('git checkout master'.split())
        self.assertTrue(p.status == 0, p.image)

        # Push branch master.
        p = Run(['git', 'push', 'origin', 'master'])
        expected_out = """\
remote: *** !!! %(TEST_DIR)s/email_to.py failed with error code: 3.
remote: *** !!! %(TEST_DIR)s/email_to.py failed with error code: 3.
remote: *** !!! %(TEST_DIR)s/email_to.py failed with error code: 3.
remote: *** !!! %(TEST_DIR)s/email_to.py failed with error code: 3.
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To:
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
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To:
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
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To:
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
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To:
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
   ab5227e..0ed035c  master -> master
""" % {'TEST_DIR': TEST_DIR}
        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
