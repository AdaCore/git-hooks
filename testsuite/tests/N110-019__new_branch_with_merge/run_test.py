def test_push_commit_on_master(testcase):
    """Push new branch wavefront (one of the commits is a merge commit)."""
    p = testcase.run("git push origin wavefront".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `c.txt'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: commits@example.com
remote: Subject: [repo] Created branch 'wavefront'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/heads/wavefront
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 3373422d2112eb335512f72cfbc59df0ae78506f
remote:
remote: The branch 'wavefront' was created pointing to:
remote:
remote:  3373422... today's resync from fsf-master. Mostly to get c.txt.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   3373422... today's resync from fsf-master. Mostly to get c.txt.
remote:   3d11ecb... c.txt: Explain why it's a great file. (*)
remote:   e4f4d53... New file: c.txt (currently nearly empty). (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: commits@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/wavefront] today's resync from fsf-master. Mostly to get c.txt.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/wavefront
remote: X-Git-Oldrev: 17edc77b55f058bedc97e7db2e35b21250bef8b3
remote: X-Git-Newrev: 3373422d2112eb335512f72cfbc59df0ae78506f
remote:
remote: commit 3373422d2112eb335512f72cfbc59df0ae78506f
remote: Merge: 17edc77 3d11ecb
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jan 10 16:44:24 2014 +0400
remote:
remote:     today's resync from fsf-master. Mostly to get c.txt.
remote:
remote: Diff:
remote: ---
remote:  c.txt | 2 ++
remote:  1 file changed, 2 insertions(+)
To ../bare/repo.git
 * [new branch]      wavefront -> wavefront
"""
    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
