# Define new classes deriving from AbstractUpdate.
# Normally, that new class is expected to override
# a certain number of methods.  The purpose of this test
# is to verify that an exception is raised if these methods
# are called in a child class that failed to provide new
# implementations.

from updates import AbstractUpdate, RefKind


class MissingSelfSanityCheck(AbstractUpdate):
    pass


class MissingOtherMethods(AbstractUpdate):
    def self_sanity_check(self):
        pass


try:
    MissingSelfSanityCheck(
        "refs/heads/master",
        RefKind.branch_ref,
        "commit",
        "0000000000000000000000000000000000000000",
        "d065089ff184d97934c010ccd0e7e8ed94cb7165",
        None,
        None,
    )
    print("*** Exception not raised in MissingSelfSanityCheck init")
except AssertionError:
    print("+++ Correct exception raised in MissingSelfSanityCheck init")
except Exception:
    print("*** Wrong exception raised in MissingSelfSanityCheck init")

bad_update = MissingOtherMethods(
    "refs/heads/master",
    RefKind.branch_ref,
    "commit",
    "0000000000000000000000000000000000000000",
    "d065089ff184d97934c010ccd0e7e8ed94cb7165",
    None,
    None,
)

try:
    bad_update.validate_ref_update()
    print("*** Exception not raised in call to validate_ref_update()")
except AssertionError:
    print("+++ Correct exception raised in call to validate_ref_update()")
except Exception:
    print("*** Wrong exception raised in call to validate_ref_update()")

try:
    bad_update.get_update_email_contents()
    print("*** Exception not raised in call to get_update_email_contents()")
except AssertionError:
    print("+++ Correct exception raised in call to get_update_email_contents()")
except Exception:
    print("*** Wrong exception raised in call to get_update_email_contents()")
