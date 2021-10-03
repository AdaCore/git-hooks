"""A module to send emails...
"""
from __future__ import print_function
from errors import InvalidUpdate
from io_utils import encode_utf8, safe_decode
import os
from subprocess import Popen, PIPE, STDOUT


def get_sendmail_exe():
    """Which sendmail program to use to send emails.

    Returns a string with the fullpath to the sendmail program to use
    in order to send emails.

    An InvalidUpdate is raised should no sendmail program be found
    (including when GIT_HOOKS_SENDMAIL is defined).

    Normally, a hardcoded list of paths is used to locate sendmail.
    However, in order to support testing where we don't want emails
    to actually be sent, the hardcoded list can be overrided via
    the GIT_HOOKS_SENDMAIL environment variable. When defined,
    its value indicate the path to sendmail to use.
    """
    all_possible_locations = ("/usr/lib/sendmail", "/usr/sbin/sendmail")

    location_override = os.environ.get("GIT_HOOKS_SENDMAIL")
    if location_override is not None:
        all_possible_locations = (location_override,)
    elif "GIT_HOOKS_TESTSUITE_MODE" in os.environ:
        # In testsuite mode, we don't want emails to be sent at all,
        # which means GIT_HOOKS_SENDMAIL must also be defined.
        # Otherwise, it means we'd be using the real sendmail,
        # thus sending emails for real, which we do not want.
        if location_override is None:
            raise InvalidUpdate(
                "The GIT_HOOKS_TESTSUITE_MODE environment variable is set,",
                "indicating that you are running the hooks in testsuite mode.",
                "In this mode, you must also define the GIT_HOOKS_SENDMAIL",
                "environment variable, pointing to a program to be called",
                "in place of the real sendmail.",
                "",
                "The goal is to catch situations where you forgot to",
                "prevent emails from being sent while using the hooks",
                "in a testing environment.",
            )

    for sendmail in all_possible_locations:
        if os.path.exists(sendmail):
            return sendmail

    # No sendmail found. Raise an error.
    err_msg = (
        ["Cannot find sendmail at either of the following locations:"]
        + [" - {loc}".format(loc=loc) for loc in all_possible_locations]
        + [
            "",
            "Please contact your system administrator.",
        ]
    )
    raise InvalidUpdate(*err_msg)


def sendmail(from_email, to_emails, mail_as_string, smtp_server):
    """Send an email with sendmail.

    PARAMETERS
      from_email: the address sending this email (e.g. user@example.com)
      to_emails: A list of addresses to send this email to.
      mail_as_string: the message to send (with headers)

    RETURNS
      A boolean (sent / not sent)

    REMARKS
        We prefer running sendmail over using smtplib because
        sendmail queues the email and retries a few times if
        the target server is unable to receive the email.
    """
    sendmail = get_sendmail_exe()

    p = Popen([sendmail] + to_emails, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    out, _ = p.communicate(encode_utf8(mail_as_string))
    if p.returncode != 0 or "GIT_HOOKS_TESTSUITE_MODE" in os.environ:
        print(safe_decode(out))
    return p.returncode == 0
