
    def test_push_notes(testcase):
        """Try pushing our notes."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin notes/commits".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":