def test_push_notes(testcase):
    """Try pushing our notes."""
    # Try pushing the notes.  The problem is that the one note
    # that needs to be pushed references a commit from master
    # which has not been pushed, yet.  So the update should be
    # rejected.
    p = testcase.run("git push origin notes/commits".split())
    expected_out = """\
remote: *** The commit associated to the following notes update
remote: *** cannot be found. Please push your branch commits first
remote: *** and then push your notes commits.
remote: ***
remote: *** Notes commit:     11ac89eb07a6ed56f971be6c4be05adb34518caa
remote: *** Annotated commit: 6d8e772f9b53f18cf9d4606296836f2a87289e34
remote: ***
remote: *** Notes contents:
remote: *** Annotating an unpushed commit...
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits -> refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
