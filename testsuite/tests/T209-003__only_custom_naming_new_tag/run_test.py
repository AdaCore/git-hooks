from support import *
import re


class TestRun(TestCase):
    def test_push_annotated_tag_std_namespace(testcase):
        # Try pushing tag v0.1. This repository is configured to ignore
        # the standard naming scheme for reference, so this should be
        # rejected as "not recognized".

        p = testcase.run("git push origin v0.1".split())
        expected_out = """\
remote: *** Unable to determine the type of reference for: refs/tags/v0.1
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/.*
remote: ***       refs/meta/.*
remote: ***       refs/drafts/.*
remote: ***       refs/for/.*
remote: ***       refs/publish/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/vendor/.*/tags/.*
remote: ***       refs/user/.*/tags/.*
remote: error: hook declined to update refs/tags/v0.1
To ../bare/repo.git
 ! [remote rejected] v0.1 -> v0.1 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_annotated_tag_custom_namespace(testcase):
        # Try pushing tag v0.1.
        p = testcase.run("git push origin v0.1:refs/user/myself/tags/v0.1".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@example.com>
remote: To: testsuite@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Created tag 'myself/tags/v0.1' in namespace 'refs/user'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@example.com>
remote: X-Git-Refname: refs/user/myself/tags/v0.1
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: c4c1e91cddc3d48a2aab7d454bc6537149f37dd8
remote:
remote: The unsigned tag 'myself/tags/v0.1' in namespace 'refs/user' was created pointing to:
remote:
remote:  8b9a0d6... New file: a.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Tue Jun 26 07:51:14 2012 -0700
remote:
remote:     This is a new tag.
To ../bare/repo.git
 * [new branch]      v0.1 -> refs/user/myself/tags/v0.1
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_push_annotated_tag_custom_namespace_not_recognized(testcase):
        # Try pushing tag v0.1.
        p = testcase.run("git push origin v0.1:refs/nogo/tags/v0.1".split())
        expected_out = """\
remote: *** Unable to determine the type of reference for: refs/nogo/tags/v0.1
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/.*
remote: ***       refs/meta/.*
remote: ***       refs/drafts/.*
remote: ***       refs/for/.*
remote: ***       refs/publish/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/vendor/.*/tags/.*
remote: ***       refs/user/.*/tags/.*
remote: error: hook declined to update refs/nogo/tags/v0.1
To ../bare/repo.git
 ! [remote rejected] v0.1 -> refs/nogo/tags/v0.1 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
