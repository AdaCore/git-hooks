
    def test_push_tag(testcase):
        """Try pushing a new value for an annotated tag."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push --force origin full-tag".split())
        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push --force origin" " full-tag:refs/user/myself/tags/full-tag".split()
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push --force origin" " full-tag:refs/nogo/myself/tags/full-tag".split()
        )
        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":