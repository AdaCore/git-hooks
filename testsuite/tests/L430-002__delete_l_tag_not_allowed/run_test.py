import re


def test_delete_lightweight_tag(testcase):
    """Try deleting a lightweight tag."""
    p = testcase.run("git push origin :some-tag".split())
    testcase.assertNotEqual(p.status, 0, p.image)

    expected_out = """\
remote: *** Deleting a tag is not allowed in this repository
remote: error: hook declined to update refs/tags/some-tag
To ../bare/repo.git
 ! [remote rejected] some-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertRunOutputEqual(p, expected_out)
