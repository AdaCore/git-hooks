from support import *

import os
from shutil import copy


class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try an update when update-hook points to a non-existant script."""
        # First, adjust the project.config file to use an update-hook
        # script.  We have to do it manually here because we want to
        # provide a name of a script we are sure does not exist.
        bad_update_hook_filename = os.path.abspath("bad-update-hook")
        assert not os.path.exists(bad_update_hook_filename)

        with open("%s/hooks_config" % TEST_DIR) as f:
            project_config = f.read() % {"hook_filename": bad_update_hook_filename}
        with open(os.path.join(testcase.repo_dir, "project.config"), "w") as f:
            f.write(project_config)
        p = testcase.run(
            ["git", "commit", "-m", "Add hooks.update-hook config", "project.config"]
        )
        assert p.status == 0, p.image

        # If we try to push this commit to refs/meta/config,
        # it should be rejected, since it introduces a config to
        # an invalid hook.
        p = testcase.run(
            ["git", "push", "origin", "refs/heads/meta/config:refs/meta/config"]
        )
        expected_out = """\
remote: *** Invalid hooks.update-hook configuration ({hook_filename}):
remote: [Errno 2] No such file or directory
remote: error: hook declined to update refs/meta/config
To ../bare/repo.git
 ! [remote rejected] meta/config -> refs/meta/config (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
            hook_filename=bad_update_hook_filename
        )

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Now, simulate the situation where the script exists
        # at the time the configuration change is pushed, but
        # then later removed by someone who does not realized
        # that the script is still being used...

        # For that, we need a script; re-use 'cvs_check.py', which
        # does nothing.
        copy(os.path.join(TEST_DIR, "cvs_check.py"), bad_update_hook_filename)
        assert os.path.exists(bad_update_hook_filename)

        # Try pushing the config update again. This time, it should work.

        p = testcase.run(
            ["git", "push", "origin", "refs/heads/meta/config:refs/meta/config"]
        )
        assert p.status == 0, p.image

        # And now that the configuration change is in, let's delete
        # bad_update_hook_filename, to see what happens when it's missing...

        os.remove(bad_update_hook_filename)
        assert not os.path.exists(bad_update_hook_filename)

        # Try to push master. It should be rejected.

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** Invalid hooks.update-hook configuration ({hook_filename}):
remote: [Errno 2] No such file or directory
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
            hook_filename=bad_update_hook_filename
        )

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
