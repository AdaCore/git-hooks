
    def test_push_note(testcase):
        """Try pushing our latest git note."""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin notes/commits".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":