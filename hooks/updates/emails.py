"""Email helpers for sending update-related emails."""

from email.utils import parseaddr, getaddresses
import os
import smtplib
from utils import debug

# All commit emails should be sent to the following email address
# for filing/archiving purposes...
FILER_EMAIL='file-ci@gnat.com'

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



