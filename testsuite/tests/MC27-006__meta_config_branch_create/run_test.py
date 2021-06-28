
    def __bare_repo_fixup(testcase):
        check_call(
            "git update-ref -d refs/meta/config".split(),
            cwd="%s/bare/repo.git" % TEST_DIR,
        )
    def test_push_commit_on_master(testcase):
        """Test creating the refs/meta/config branch on the remote."""
        testcase.__bare_repo_fixup()
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin meta/config:refs/meta/config".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":