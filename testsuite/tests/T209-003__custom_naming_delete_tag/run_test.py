from support import *
import re

class TestRun(TestCase):
    def test_push_annotated_tag(self):
        """Try pushing an annotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Delete a tag in the standard naming scheme.

        p = Run('git push origin :full-tag'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
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

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Same as above: Try deleting a tag, except we are passing
        # the tag's full reference name instead of just passing
        # the tag's name.

        p = Run('git push origin :refs/tags/other-full-tag'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
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

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Delete a tag with a custom reference name which is recognized
        # as a tag reference.

        p = Run('git push origin :refs/vendor/me/tags/v1'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: repo@example.com
remote: Subject: [repo] Deleted tag 'me/tags/v1' in namespace 'refs/vendor'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/vendor/me/tags/v1
remote: X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The annotated tag 'me/tags/v1' in namespace 'refs/vendor' was deleted.
remote: It previously pointed to:
remote:
remote:  354383f... Initial commit.
To ../bare/repo.git
 - [deleted]         refs/vendor/me/tags/v1
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Delete a custom reference name which is recognized as a tag,
        # but does not exist on the remote.

        p = Run('git push origin :refs/vendor/me/tags/unknown'.split())
        expected_out = """\
remote: *** unable to delete 'refs/vendor/me/tags/unknown': remote ref does not exist
remote: error: hook declined to update refs/vendor/me/tags/unknown
To ../bare/repo.git
 ! [remote rejected] refs/vendor/me/tags/unknown (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
