def test_git_config(testcase):
    """Unit test AbstractUpdate child class missing methods."""
    testcase.run_unit_test_script(
        expected_out="""\
+++ Correct exception raised in MissingSelfSanityCheck init
+++ Correct exception raised in call to validate_ref_update()
+++ Correct exception raised in call to get_update_email_contents()
"""
    )
