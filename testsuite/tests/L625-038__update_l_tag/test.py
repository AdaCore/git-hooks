from support import *

class TestRun(TestCase):
    def test_delete_lightweight_tag(self):
        """Try updating a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(1)

        p = Run('git push origin some-tag'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/some-tag, 8b9a0d6bf08d7a983affbee3c187adadaaedec9e, 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5)
remote: *** ---------------------------------------------------------------
remote: *** --  IMPORTANT NOTICE:
remote: *** --
remote: *** --  You just updated the "some-tag" tag as follow:
remote: *** --    old SHA1: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: *** --    new SHA1: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote: *** --
remote: *** -- Other developers pulling from this repository will not
remote: *** -- get the new tag. Assuming this update was deliberate,
remote: *** -- notifying all known users of the update is recommended.
remote: *** ---------------------------------------------------------------
remote: DEBUG: update base: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=8b9a0d6bf08d7a983affbee3c187adadaaedec9e, new_rev=8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5)
remote: *** cvs_check: `trunk/repo/a'
remote: DEBUG: post_receive_one(ref_name=8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote:                         old_rev=8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote:                         new_rev=refs/tags/some-tag)
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@example.com>
remote: To: something-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated tag some-tag
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/tags/some-tag
remote: X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e
remote: X-Git-Newrev: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5
remote:
remote: The lightweight tag 'some-tag' was updated to point to:
remote:
remote:  8a567a0... Put some contents in file `a'.
remote:
remote: It previously pointed to:
remote:
remote:  8b9a0d6... New file: a.
To ../bare/repo.git
   8b9a0d6..8a567a0  some-tag -> some-tag
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
