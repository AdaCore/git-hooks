def test_post_receive_one(testcase):
    """Unit test utils.get_user_name."""
    testcase.run_unit_test_script(
        expected_out="""\
None
refs/funny
"""
    )
