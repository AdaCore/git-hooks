def test_push_annotated_tag(testcase):
    """Try pushing an annotated tag."""
    # Try deleting full-tag.  The remote is setup to refuse this request.
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Subject: [repo] Deleted tag 'full-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/tags/full-tag
remote: X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The annotated tag 'full-tag' was deleted.
remote: It previously pointed to:
remote:
remote:  354383f... Initial commit.
To ../bare/repo.git
 - [deleted]         full-tag
"""

    p = testcase.run("git push origin :full-tag".split())
    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Same as above: Try deleting a tag, except we are passing
    # the tag's full reference name instead of just passing
    # the tag's name.

    p = testcase.run("git push origin :refs/tags/other-full-tag".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Subject: [repo] Deleted tag 'other-full-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/tags/other-full-tag
remote: X-Git-Oldrev: 3649b2f18a00aa9f067a3ee2d5d76406571fd7f3
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The annotated tag 'other-full-tag' was deleted.
remote: It previously pointed to:
remote:
remote:  354383f... Initial commit.
To ../bare/repo.git
 - [deleted]         other-full-tag
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
