from support import *


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try non-fast-forward push on master."""
        p = testcase.run("git push -f origin master".split())
        expected_out = """\
remote: *** Non-fast-forward updates are not allowed for this reference.
remote: *** Please rebase your changes on top of the latest HEAD,
remote: *** and then try pushing again.
remote: ***
remote: *** Note: It looks like the hooks.non-fast-forward configuration
remote: *** for your repository is set to only match the name of the branch
remote: *** being updated (e.g. "master"), which is how this configuration
remote: *** option was originally interpreted. However, the semantics of
remote: *** this option has since been changed and its values must now match
remote: *** the reference name (e.g. "refs/heads/master"). If you believe
remote: *** this non-fast-forward update should be allowed on this branch,
remote: *** contact your repository adminstrator to review the repository's
remote: *** hooks.non-fast-forward option configuration.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
