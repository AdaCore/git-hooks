
    def test_push_commit_on_master(testcase):
        """Try pushing commit on master."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin master".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":