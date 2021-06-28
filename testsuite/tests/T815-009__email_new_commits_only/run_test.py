
    def test_push_on_branch_with_email_new_commits_only(testcase):
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin feature".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push -f origin feature-2:feature".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin feature-3:feature".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin feature-4:feature".split())
remote: ---
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin feature-no-emails".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == "__main__":