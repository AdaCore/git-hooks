
    def test_push_commit(testcase):
        """Try pushing a commit that creates a subproject."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run(["git", "submodule", "add", "%s/bare/subm.git" % TEST_DIR])
        assert p.status == 0, p.image
        assert isdir("subm"), p.image + "\n" + testcase.run(["ls -la".split()]).cmd_out
        p = testcase.run(["git", "commit", "-m", "Add submodule subm"])
        assert p.status == 0, p.image
        p = testcase.run(["git rev-parse HEAD".split()])
        assert p.status == 0, p.image
        p = testcase.run(["git log -n1 --pretty=format:%ad".split()])
        assert p.status == 0, p.image
        p = testcase.run(["git ls-tree HEAD .gitmodules".split()])
        assert p.status == 0, p.image
        del os.environ["GIT_HOOKS_STYLE_CHECKER"]
        os.environ["PATH"] = TEST_DIR + ":" + os.environ["PATH"]
        testcase.set_debug_level(2)
        p = testcase.run("git push origin master".split())
""" % {
            "subm_rev": subm_rev,
            "short_subm_rev": subm_rev[0:7],
            "author_date": author_date,
            "gitmodules_short_hash": gitmodules_hash[:7],
            "TEST_DIR": TEST_DIR,
        }
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":