from support import *


class TestRun(TestCase):
    def test_filename_collisions(testcase):
        """Test filename-collision detector."""
        cd("%s/repo" % TEST_DIR)

        # Push master to the `origin' remote.  The operation should
        # fail due to some filename collisions...
        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: *** The following filename collisions have been detected.
remote: *** These collisions happen when the name of two or more files
remote: *** differ in casing only (Eg: "hello.txt" and "Hello.txt").
remote: *** Please re-do your commit, chosing names that do not collide.
remote: ***
remote: ***     Commit: 2cb0ac93cfb4ac44db4d24973d0f13e087900cb4
remote: ***     Subject: Add new file (A).
remote: ***
remote: *** The matching files are:
remote: ***
remote: ***     A
remote: ***     a
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Same for the 'two-files' branch...
        # This example is slightly more complex, as it involves
        # two sets of files that collide, as well as a second
        # commit that does not introduce any collision.  The purpose
        # of the second commit is to verify that the hooks verify
        # *all* commits, not just the last one.
        p = testcase.run("git push origin two-files".split())
        expected_out = """\
remote: *** The following filename collisions have been detected.
remote: *** These collisions happen when the name of two or more files
remote: *** differ in casing only (Eg: "hello.txt" and "Hello.txt").
remote: *** Please re-do your commit, chosing names that do not collide.
remote: ***
remote: ***     Commit: 8666d4ae4d66cff8c036db8b75ae26dd3bf1df14
remote: ***     Subject: This commit iznogoud because colliding names...
remote: ***
remote: *** The matching files are:
remote: ***
remote: ***     README
remote: ***     readme
remote: ***
remote: ***     Hello.txt
remote: ***     hello.txt
remote: error: hook declined to update refs/heads/two-files
To ../bare/repo.git
 ! [remote rejected] two-files -> two-files (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
