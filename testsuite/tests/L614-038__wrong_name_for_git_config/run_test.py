def test_git_config(testcase):
    """Unit test git_config with invalid config name..."""
    testcase.run_unit_test_script(
        expected_out="""\
+++ Exception raised as expected.
"""
    )
