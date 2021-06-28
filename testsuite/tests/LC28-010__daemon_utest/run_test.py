from support import *


class TestRun(TestCase):
    def test_run_in_daemon_error_handling(testcase):
        """Test run_in_daemon error handling..."""
        testcase.run_unit_test_script(
            expected_out="""\
DEBUG: Test run_in_daemon failing at the first fork...
fork #1 failed: (12) fork: Resource temporarily unavailable
SYSLOG: style_checker: my message
""",
        )


if __name__ == "__main__":
    runtests()
