
    def test_push_notes(testcase):
        """Try pushing a note under refs/notes/deploy"""
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin notes/deploy".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":