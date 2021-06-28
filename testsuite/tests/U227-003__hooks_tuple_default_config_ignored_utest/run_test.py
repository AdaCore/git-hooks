from support import runtests, TestCase, TEST_DIR


class TestRun(TestCase):
    def test_git_config(testcase):
        """Unit test AbstractUpdate child class missing methods."""
        testcase.run_unit_test_script(
            expected_out="""\
DEBUG: no-emails (len = 3)
refs/heads/uninteresting
refs/no/emails
refs/what/ever
"""
        )


if __name__ == "__main__":
    runtests()
