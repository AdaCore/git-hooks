from support import *

class TestRun(TestCase):
    def test_create_retired_branch(self):
        """Try pushing the (newly-created branch) retired/gdb-5.0.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin retired/gdb-5.0'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = (
            r".*\[new branch\]\s+retired/gdb-5\.0 -> retired/gdb-5\.0" +
            ".*")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)


    def test_push_retired_branch(self):
        """Try pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*Updates to the gdb-7.5 branch are no longer allowed, " +
            r".*this branch has been retired \(and renamed into" +
              " `retired/gdb-7.5'\)" +
            r".*error: hook declined to update refs/heads/gdb-7.5" +
            ".*")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

    def test_force_push_retired_branch(self):
        """Try force-pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*Updates to the gdb-7.5 branch are no longer allowed, " +
            r".*this branch has been retired \(and renamed into" +
              " `retired/gdb-7.5'\)" +
            r".*error: hook declined to update refs/heads/gdb-7.5" +
            ".*")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

    def test_push_retired_branch_as_tag(self):
        """Try pushing a branch update on a retired branch...

        ... where the branch has been marked as retired thanks to
        a tag named retired/<branch-name>
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.6'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*Updates to the gdb-7.6 branch are no longer allowed, " +
            r".*this branch has been retired \(a tag called " +
              "`retired/gdb-7.6' has been" +
              ".* created in its place\)" +
            r".*error: hook declined to update refs/heads/gdb-7.6" +
            ".*")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

    def test_force_push_retired_branch_as_tag(self):
        """Try force-pushing a branch update on a retired branch...

        ... where the branch has been marked as retired thanks to
        a tag named retired/<branch-name>
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin gdb-7.6'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*Updates to the gdb-7.6 branch are no longer allowed, " +
            r".*this branch has been retired \(a tag called " +
              "`retired/gdb-7.6' has been" +
              ".* created in its place\)" +
            r".*error: hook declined to update refs/heads/gdb-7.6" +
            ".*")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
