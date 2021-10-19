def test_multiline_git_config(testcase):
    """Check that we handle multiline configs correctly"""
    testcase.run_unit_test_script(
        expected_out="""\
DEBUG: no-emails (len = 1)
a multiline description
of my project which should be
handled properly by the git-hooks.
""",
    )
