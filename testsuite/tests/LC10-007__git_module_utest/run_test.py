def test_git_config(testcase):
    """Unit test AbstractUpdate child class missing methods."""
    testcase.run_unit_test_script(
        cwd=testcase.repo_dir,
        expected_out="""\
DEBUG: Test the git --switch=False attribute
d065089ff184d97934c010ccd0e7e8ed94cb7165
DEBUG: A Test to verify that git does not do any lstrip-ing...
  Commit Subject starting with spaces
DEBUG: Unit test get_object_type with a null SHA1...
delete
""",
    )
