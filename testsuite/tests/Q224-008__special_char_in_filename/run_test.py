
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin master".split())
"""[
            1:
        ]  # To strip the extra newline at the start introduce for visuals only

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":