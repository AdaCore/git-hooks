def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote:
remote: commit 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat May 5 15:23:36 2012 -0700
remote:
remote:     Minor modifications.
remote:
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] 1 modified file, 1 new file.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: X-Git-Newrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote:
remote: commit 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:20:05 2012 -0700
remote:
remote:     1 modified file, 1 new file.
remote:
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Modify `c', delete `b'.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: X-Git-Newrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote:
remote: commit cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:06 2012 -0700
remote:
remote:     Modify `c', delete `b'.
remote:
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Modify file `d' alone.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: X-Git-Newrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote:
remote: commit dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:57 2012 -0700
remote:
remote:     Modify file `d' alone.
remote:
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
