
    def test_push_commit_on_master(testcase):
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin release-0.1-branch".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        cd("%s/bare/repo.git" % TEST_DIR)
        p = testcase.run("git show-ref -s release-0.1-branch".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":