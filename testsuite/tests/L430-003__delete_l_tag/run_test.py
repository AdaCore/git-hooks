from support import *


class TestRun(TestCase):
    def test_delete_lightweight_tag(testcase):
        """Try deleting a lightweight tag."""
        cd("%s/repo" % TEST_DIR)

        p = testcase.run("git push origin :some-tag".split())
        testcase.assertEqual(p.status, 0, p.image)

        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@example.com>
remote: To: something-ci@example.com
remote: Subject: [repo] Deleted tag 'some-tag'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/tags/some-tag
remote: X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The lightweight tag 'some-tag' was deleted.
remote: It previously pointed to:
remote:
remote:  8b9a0d6... New file: a.
To ../bare/repo.git
 - [deleted]         some-tag
"""

        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
