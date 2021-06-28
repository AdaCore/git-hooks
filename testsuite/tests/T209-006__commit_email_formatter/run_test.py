from support import cd, runtests, TestCase, TEST_DIR
    def test_commit_commit_email_formatter(testcase):
        cd("%s/repo" % TEST_DIR)
        p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "checkout", "FETCH_HEAD"])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            [
                "git",
                "config",
                "--file",
                "project.config",
                "hooks.commit-email-formatter",
                os.path.join(TEST_DIR, "commit-email-formatter.py"),
            ]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(
            [
                "git",
                "commit",
                "-m",
                "Add hooks.commit-email-formatter",
                "project.config",
            ]
        )
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
        testcase.assertEqual(p.status, 0, p.image)
        assert "HEAD -> refs/meta/config" in p.out.splitlines()[-1], p.image
        p = testcase.run(["git", "checkout", "master"])
        testcase.assertEqual(p.status, 0, p.image)
        p = testcase.run("git push origin master".split())
""".format(
            TEST_DIR=TEST_DIR
        )
""".format(
            TEST_DIR=TEST_DIR
        )
""".format(
            TEST_DIR=TEST_DIR
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin hook-dump".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin notes/commits".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":