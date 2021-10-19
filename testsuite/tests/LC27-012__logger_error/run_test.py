import os


def test_logger_returning_nonzero(testcase):
    testcase.run_unit_test_script(
        env={"GIT_HOOKS_LOGGER": os.path.join(testcase.work_dir, "bad-logger")},
        expected_out="""\
*** Failed to file the following syslog entry:
***   - message: some message
***   - tag: style_checker
***   - priority: local0.warn
***
*** logger returned with error code 1:
*** Error trying to connect to syslog server:
*** Connection reset by peer
""",
    )
