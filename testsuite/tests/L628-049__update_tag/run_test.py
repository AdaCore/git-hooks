
    def test_push_tag(testcase):
        """Try pushing a new value for an annotated tag."""
        cd("%s/repo" % TEST_DIR)
        testcase.set_debug_level(1)
        p = testcase.run("git push --force origin full-tag".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":