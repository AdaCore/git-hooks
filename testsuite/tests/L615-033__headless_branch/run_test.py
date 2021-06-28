
    def test_push(testcase):
        cd("%s/repo" % TEST_DIR)
        testcase.set_debug_level(1)
        p = testcase.run("git push origin headless".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin one-commit".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":