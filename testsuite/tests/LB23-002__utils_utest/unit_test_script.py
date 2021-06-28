import os

from utils import get_user_name, get_user_full_name

# Call get_user_name with the GIT_HOOKS_USER_NAME environment variable
# being unset. The value being returned is not important and dependent
# on the user running the testsuite, so we don't check it.
del os.environ["GIT_HOOKS_USER_NAME"]
assert get_user_name() is not None

# Same as above, but calling get_user_full_name after having unset
# the GIT_HOOKS_USER_FULL_NAME environment variable.
del os.environ["GIT_HOOKS_USER_FULL_NAME"]
assert get_user_full_name() is not None

# Try calling get_user_full_name again, but this time after having set
# the GIT_HOOKS_USER_FULL_NAME environment variable to a string which
# contains both full name and email address.
os.environ["GIT_HOOKS_USER_FULL_NAME"] = "John Smith  <j.smith@example.com> "
print(get_user_full_name())
