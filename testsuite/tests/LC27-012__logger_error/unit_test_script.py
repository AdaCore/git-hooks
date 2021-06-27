# The unit-test script to be called by the testcase script (run_test.py).
# It's only role is to import and call the git-hooks' "syslog" function.
# The testcase script itself has set the environment up to make that
# function behave the way we want to (namely, have that function report
# an error).

from syslog import syslog

syslog("some message")
