"""Email helpers for sending update-related emails."""

from config import git_config
from email.utils import parseaddr, getaddresses
from git import get_module_name
import os
import smtplib
from utils import debug, InvalidUpdate, get_user_name, get_user_full_name

# All commit emails should be sent to the following email address
# for filing/archiving purposes...
FILER_EMAIL='file-ci@gnat.com'

class EmailInfo(object):
    """Aggregates various pieces of info needed to send emails.

    ATTRIBUTES
        project_name: The name of the project (usually, the name of
            the directory holding the git repository).
        email_from: The email address to use in the From: field
            when sending the email notification.
        email_to: The email addresses, in RFC 822 format, of the
            recipients of the email notification.

    REMARKS
        This hoosk assumes that the hooks.fromdomain config parameter
        is set.  Otherwise, an InvalidUpdate exception is raised when
        the object is initialized.
    """
    def __init__(self):
        self.project_name = get_module_name()

        from_domain = git_config('hooks.fromdomain')
        if not from_domain:
            raise InvalidUpdate(
                'Error: hooks.fromdomain config variable not set.',
                'Cannot send email notifications.')
        self.email_from = '%s <%s@%s>' % (get_user_full_name(),
                                          get_user_name(),
                                          from_domain)

        self.email_to = git_config('hooks.mailinglist')
        if not self.email_to:
            # We should really raise an error if this config variable is
            # not set.  But since emailing occurs after the update
            # has already been made, error-ing out would not actually
            # help at all.  Do the best we can, which is trying to file
            # the commits, and also warn the user about it.
            print "---------------------------------------------------------"
            print "-- WARNING:"
            print "-- The hooks.mailinglist config variable not set."
            print "-- Commit emails will only be sent to %s." % FILER_EMAIL
            print "---------------------------------------------------------"
            self.email_to=FILER_EMAIL


def send_email(e_msg):
    """Send the given e_msg.

    PARAMETERS
        e_msg: An email.message.Message object.
    """
    email_from = parseaddr(e_msg.get('From'))
    email_recipients = [addr[1] for addr
                        in getaddresses(e_msg.get_all('To', [])
                                        + e_msg.get_all('Cc', [])
                                        + e_msg.get_all('Bcc', []))]

    if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
        # Use debug level 0 to make sure that the trace is always
        # printed.
        debug(e_msg.as_string(), level=0)
    else: # pragma: no cover (do not want to send real emails during testing)
        s = smtplib.SMTP('localhost')
        s.sendmail(email_from, email_recipients, e_msg.as_string())
        s.quit()



