    def test_push_commits_on_master(testcase):
        cd("%s/repo" % TEST_DIR)
        p = testcase.run("git push origin meta-config-missing:refs/meta/config".split())
        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin meta-config:refs/meta/config".split())
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run("git push origin step-1/checker_config_missing:master".split())
        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push origin step-2/add_checker_config_file:master".split()
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push origin step-3/try_initial_commit_again:master".split()
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push origin step-4/modify_checker_config_only:master".split()
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
        p = testcase.run(
            "git push origin step-5/modify_code_and_checker_config:master".split()
        )
        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)
if __name__ == "__main__":