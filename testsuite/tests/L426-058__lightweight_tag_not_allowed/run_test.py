def has_rejection(out, tag_name):
    if "Lightweight tags (%s) are not allowed in this repository" % tag_name not in out:
        return False
    if "error: hook declined to update" not in out:
        return False
    return True


def test_push_lightweight_tag(testcase):
    """Try pushing an lightweight tag."""
    # Create a tag called 'new-tag'...
    p = testcase.run("git tag new-tag".split())
    testcase.assertEqual(p.status, 0, p.image)

    # Try pushing that new-tag.  The repository has been configured
    # to reject such updates.
    p = testcase.run("git push origin new-tag".split())
    testcase.assertNotEqual(p.status, 0, p.image)

    expected_out = """\
remote: *** Lightweight tags ('new-tag') are not allowed in this repository.
remote: *** Use 'git tag [ -a | -s ]' for tags you want to propagate.
remote: error: hook declined to update refs/tags/new-tag
To ../bare/repo.git
 ! [remote rejected] new-tag -> new-tag (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertRunOutputEqual(p, expected_out)
