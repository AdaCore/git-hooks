
    def test_push_head(testcase):
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin head".split())
remote: ---
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)
        cd("%s/bare/repo.git" % TEST_DIR)
        p = testcase.run("git show-ref -s head".split())
        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":