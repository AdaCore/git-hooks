    def test_pushes(testcase):
        """Test various pushes to multi-project repository."""
        cd("%s/repo" % TEST_DIR)
        with open("%s/hooks_config" % TEST_DIR) as f:
            project_config = f.read() % {"TEST_DIR": TEST_DIR}
        with open("project.config", "w") as f:
        p = testcase.run(
            ["git", "commit", "-m", "fix hooks.mailinglist", "project.config"]
        )
        assert p.status == 0, p.image
        p = testcase.run(
            ["git", "push", "origin", "refs/heads/meta/config:refs/meta/config"]
        )
        assert p.status == 0, p.image
        p = testcase.run("git checkout master".split())
        assert p.status == 0, p.image
        p = testcase.run(
            ["git", "push", "origin", "4207b94cadc3c1be0edb4f6df5670f0311c267f3:master"]
        )
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            ["git", "push", "origin", "cd2f5d40776eee5a47dc821eddd9a7c6c0ed436d:master"]
        )
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            ["git", "push", "origin", "4c7588eee23d6d42e8d50ba05343e3d0f31dd286:master"]
        )
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            ["git", "push", "origin", "0ed035c4417a51987594586016b061bed362ec9b:master"]
        )
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(["git", "push", "origin", "master"])
remote: ---
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(["git", "push", "origin", "bfd-tag"])
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(["git", "push", "origin", "gdb-tag"])
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(["git", "push", "origin", "common-tag"])
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            ["git", "push", "origin", "refs/notes/commits:refs/notes/commits"]
        )
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":