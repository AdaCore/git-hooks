def test_update_branch_custom_name_not_recognized(testcase):
    """Push a branch updates using invalid custom reference names."""
    # Push to a reference which does exist in the remote repository,
    # but does not follow any of the repository's naming schemes.
    p = testcase.run(
        "git push origin my-topic:refs/others/exists-but-unrecognized".split()
    )
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/others/exists-but-unrecognized
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
remote: ***       refs/vendor/.*
remote: ***       refs/user/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/tags/.*
remote: error: hook declined to update refs/others/exists-but-unrecognized
To ../bare/repo.git
 ! [remote rejected] my-topic -> refs/others/exists-but-unrecognized (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Push to a reference which does not exist in the remote
    # repository, and whose name does not follow any of the
    # repository's naming schemes.
    p = testcase.run("git push origin my-topic:refs/does-not-exist/my-feature".split())
    expected_out = """\
remote: *** Unable to determine the type of reference for: refs/does-not-exist/my-feature
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
remote: ***       refs/vendor/.*
remote: ***       refs/user/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/tags/.*
remote: error: hook declined to update refs/does-not-exist/my-feature
To ../bare/repo.git
 ! [remote rejected] my-topic -> refs/does-not-exist/my-feature (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
