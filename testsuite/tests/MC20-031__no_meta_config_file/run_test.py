from support import *
from subprocess import check_output, check_call


class TestRun(TestCase):
    def __bare_repo_fixup(testcase):
        """Fix the bare repository to implement legacy hooks configuration.

        Reproduce the (legacy) situation where the project.config file
        in refs/meta/config does not exist, and where the repository's
        hooks configuration is stored inside the repository's config
        file.
        """
        # First, extract the configuration, available at the standard
        # location.
        cfg_txt = check_output(
            "git show refs/meta/config:project.config".split(),
            cwd=testcase.bare_repo_dir,
        )
        with open(os.path.join(testcase.bare_repo_dir, "config"), "a") as f:
            f.write(cfg_txt)
        check_call(
            "git update-ref -d refs/meta/config".split(),
            cwd=testcase.bare_repo_dir,
        )

    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master."""
        testcase.__bare_repo_fixup()

        cd("%s/repo" % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** -----------------------------------------------------------------
remote: *** Unable to find the file project.config in refs/meta/config.
remote: ***
remote: *** Your repository appears to be incorrectly set up. Please contact
remote: *** your repository's administrator to set your project.config file up.
remote: *** -----------------------------------------------------------------
To ../bare/repo.git
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
