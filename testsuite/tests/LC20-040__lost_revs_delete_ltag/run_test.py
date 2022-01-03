def test_delete_tag(testcase):
    """Delete a lightweight tag causing multiple commits to be lost."""
    p = testcase.run("git push origin :retired/gdb-7.2".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted tag 'retired/gdb-7.2'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/retired/gdb-7.2
remote: X-Git-Oldrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The lightweight tag 'retired/gdb-7.2' was deleted.
remote: It previously pointed to:
remote:
remote:  dd6165c... Modify file `d' alone.
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   dd6165c... Modify file `d' alone.
remote:   cc8d2c2... Modify `c', delete `b'.
remote:   4a325b3... 1 modified file, 1 new file.
remote:   4f0f08f... Minor modifications.
To ../bare/repo.git
 - [deleted]         retired/gdb-7.2
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
