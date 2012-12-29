"""Email helpers for sending update-related emails."""

from config import git_config
from email.mime.text import MIMEText
from email.utils import parseaddr, getaddresses
from errors import InvalidUpdate
from git import get_module_name
import os
from utils import debug, get_user_name, get_user_full_name

try:
    from gnatpython.sendmail import sendmail
except ImportError: # pragma: no cover (testing requires recent version)
    # gnatpython is not recent enough, and is missing this module.
    # Use the copy we saved in our repository.
    from updates.sendmail import sendmail

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
        has_mailinglist_config: True iff the 'hooks.mailinglist'
            git config parameter is set for this project.

    REMARKS
        This class assumes that the hooks.from-domain config parameter
        is set.  Otherwise, an InvalidUpdate exception is raised when
        the object is initialized.
    """
    def __init__(self):
        """The constructor.

        PARAMETERS
            print_warnings: If True, then emit warnings.
        """
        self.project_name = get_module_name()

        from_domain = git_config('hooks.from-domain')
        if not from_domain:
            raise InvalidUpdate(
                'Error: hooks.from-domain config variable not set.',
                'Please contact your repository\'s administrator.')
        self.email_from = '%s <%s@%s>' % (get_user_full_name(),
                                          get_user_name(),
                                          from_domain)

        self.email_to = git_config('hooks.mailinglist')
        self.has_mailinglist_config = bool(self.email_to)
        if not self.has_mailinglist_config:
            # We should really raise an error if this config variable is
            # not set.  But since emailing occurs after the update
            # has already been made, error-ing out would not actually
            # help at all.  Do the best we can, which is trying to file
            # the commits.
            self.email_to=FILER_EMAIL


class Email(object):
    """An email object.

    All emails to be sent by the git-hooks should be sent via
    this class to ensure consistency.

    ATTRIBUTES
        e_msg: An email.mime.text.MIMEText object.
    """
    def __init__(self, email_info, email_subject, email_body,
                 ref_name, old_rev, new_rev, diff=None):
        """The constructor.

        PARAMETERS
            email_info: An EmailInfo object.
            email_subject: The email's subject.
            email_body: The email's body.
            ref_name: See AbstractUpdate.ref_name attribute.
            old_rev: See AbstractUpdate.old_rev attribute.
            new_rev: See AbstractUpdate.new_rev attribute.
            diff: A diff string, if applicable.  Otherwise None.
                When not None, the diff is appended at the end
                of the email's body - truncated if necessary.
        """
        if diff is not None:
            # Append the "Diff:" marker to email_body, followed by
            # the diff. Truncate the patch if necessary.
            max_diff_size = git_config('hooks.max-email-diff-size')
            if len(diff) > max_diff_size:
                diff = diff[:max_diff_size]
                diff += '\n\n[diff truncated at %d bytes]\n' % max_diff_size
            email_body += '\nDiff:\n'
            email_body += diff

        self.e_msg = MIMEText(email_body)

        # Create the email's header.
        self.e_msg['From'] = email_info.email_from
        self.e_msg['To'] = email_info.email_to
        if git_config('hooks.bcc-file-ci'):
            self.e_msg['Bcc'] = FILER_EMAIL
        self.e_msg['Subject'] = email_subject
        self.e_msg['X-ACT-checkin'] = email_info.project_name
        self.e_msg['X-Git-Refname'] = ref_name
        self.e_msg['X-Git-Oldrev'] = old_rev
        self.e_msg['X-Git-Newrev'] = new_rev

    def send(self):
        """Send this email.

        REMARKS
            If the GIT_HOOKS_TESTSUITE_MODE environment variable
            is set, then a trace of the email is printed, instead
            of sending it.  This is for testing purposes.
        """
        email_from = self.e_msg.get('From')
        email_recipients = [addr[1] for addr
                            in getaddresses(self.e_msg.get_all('To', [])
                                            + self.e_msg.get_all('Cc', [])
                                            + self.e_msg.get_all('Bcc', []))]

        if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
            # Use debug level 0 to make sure that the trace is always
            # printed.
            debug(self.e_msg.as_string(), level=0)
        else: # pragma: no cover (do not want real emails during testing)
            # Use gnatpython's sendmail module rather than Python's
            # smtplib, because the latter does everything synchronously,
            # which takes time, and also does not handle queueing.
            sendmail(email_from, email_recipients, self.e_msg.as_string(),
                     'localhost')
