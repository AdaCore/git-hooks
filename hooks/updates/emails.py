"""Email helpers for sending update-related emails."""

from config import git_config
from email.mime.text import MIMEText
from email.utils import getaddresses
from errors import InvalidUpdate
from git import get_module_name
import os
from string import strip
from time import sleep
from updates.sendmail import sendmail
from utils import debug, get_user_name, get_user_full_name

# All commit emails should be sent to the following email address
# for filing/archiving purposes...
FILER_EMAIL = 'file-ci@gnat.com'

# The delay (in seconds) between each email being sent out.
# The purpose of the delay is to help separate each email
# in time, in order to increase our chances of having each
# one of them delivered in order.
EMAIL_DELAY_IN_SECONDS = 5


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
        This class assumes that the hooks.from-domain config parameter
        is set.  Otherwise, an InvalidUpdate exception is raised when
        the object is initialized.
    """
    def __init__(self, email_from):
        """The constructor.

        PARAMETERS
            email_from: If not None, a string that provides the email
                address of the sender.  Eg: 'David Smith <ds@example.com>'.
                If None, this address is computed from the environment.
        """
        self.project_name = get_module_name()

        from_domain = git_config('hooks.from-domain')
        if not from_domain:
            raise InvalidUpdate(
                'Error: hooks.from-domain config variable not set.',
                'Please contact your repository\'s administrator.')
        if email_from is None:
            self.email_from = '%s <%s@%s>' % (get_user_full_name(),
                                              get_user_name(),
                                              from_domain)
        else:
            self.email_from = email_from

        self.email_to = git_config('hooks.mailinglist')
        if not self.email_to:
            raise InvalidUpdate(
                'Error: hooks.mailinglist config option not set.',
                'Please contact your repository\'s administrator.')


class EmailQueue(object):
    """An email queue (a singleton).

    ATTRIBUTES
        queue: A list of emails to be sent.
    """
    def __new__(cls, *args, **kw):
        """The allocator."""
        if not hasattr(cls, '_instance'):
            orig = super(EmailQueue, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        """The constructor."""
        # If the singleton has never been initialized, do it now.
        if not hasattr(self, 'queue'):
            self.queue = []

    def enqueue(self, email):
        """Enqueue the given email.

        PARAMETERS
            email: An Email object.
        """
        self.queue.append(email)

    def flush(self):
        """Send all enqueued emails...

        ... in the same order that they were enqueued.  A delay
        of EMAIL_DELAY_IN_SECONDS is also introduced between
        emails.

        REMARKS
            If the GIT_HOOKS_TESTSUITE_MODE environment variable
            is set, then a trace of the delay is printed, instead
            of actually delaying the execution.  Since emails are
            not actually sent when in GIT_HOOKS_TESTSUITE_MODE,
            there is no point in waiting for this delay.
        """
        nb_emails_left = len(self.queue)
        for email in self.queue:
            email.send()
            nb_emails_left -= 1
            if nb_emails_left > 0:
                # Need a small delay until we can send the next one.
                if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
                    # For the testsuite, print a debug trace in place
                    # of delaying the execution.  Use debug level 0
                    # to make sure it is always printed (to make sure
                    # the testsuite always alerts us if there is any
                    # change in the delay policy).
                    debug('inter-email delay...', level=0)
                else:  # pragma: no cover (do not want delays during testing)
                    sleep(EMAIL_DELAY_IN_SECONDS)
        self.queue = []


class Email(object):
    """An email object.

    All emails to be sent by the git-hooks should be sent via
    this class to ensure consistency.

    ATTRIBUTES
        email_info: An EmailInfo object.
        email_subject: The email's subject.
        email_body: The email's body, possibly including a diff
            at the end (see __init__ method).
        send_to_filer: A boolean, True if the email should be sent to
            FILER_EMAIL, False otherwise.  The default should always
            be to copy FILER_EMAIL, unless proven otherwise.
        author: A string in "name <email>" format, to be used as
            the X-Git-Author field in the email header. May be None,
            in which case we'll use email_info.email_from instead.
        ref_name: See AbstractUpdate.ref_name attribute.
        old_rev: See AbstractUpdate.old_rev attribute.
        new_rev: See AbstractUpdate.new_rev attribute.
    """
    def __init__(self, email_info, email_subject, email_body,
                 author, ref_name, old_rev, new_rev, diff=None,
                 send_to_filer=True):
        """The constructor.

        PARAMETERS
            email_info: Same as the attribute.
            email_subject: Same as the attribute.
            email_body: Same as the attribute.
            author: Same as the attribute.
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
            diff: A diff string, if applicable.  Otherwise None.
                When not None, the diff is appended at the end
                of the email's body - truncated if necessary.
            send_to_filer: Same as the attribute.
        """
        if diff is not None:
            # Append the "Diff:" marker to email_body, followed by
            # the diff. Truncate the patch if necessary.
            max_diff_size = git_config('hooks.max-email-diff-size')
            if len(diff) > max_diff_size:
                diff = diff[:max_diff_size]
                diff += ('[...]\n\n[diff truncated at %d bytes]\n'
                         % max_diff_size)

            email_body += '\nDiff:\n'
            email_body += diff

        self.email_info = email_info
        self.email_subject = email_subject
        self.email_body = email_body
        self.send_to_filer = send_to_filer
        self.author = author
        self.ref_name = ref_name
        self.old_rev = old_rev
        self.new_rev = new_rev

    def enqueue(self):
        """Enqueue this email in the EmailQueue.

        REMARKS
            This is mostly a convenience method.
        """
        EmailQueue().enqueue(self)

    def send(self):
        """Send this email.

        REMARKS
            If the GIT_HOOKS_TESTSUITE_MODE environment variable
            is set, then a trace of the email is printed, instead
            of sending it.  This is for testing purposes.
        """
        e_msg = MIMEText(self.email_body)

        # Create the email's header.
        e_msg['From'] = self.email_info.email_from
        e_msg['To'] = ', '.join(map(strip, self.email_info.email_to))
        if self.send_to_filer and git_config('hooks.bcc-file-ci'):
            e_msg['Bcc'] = FILER_EMAIL
        e_msg['Subject'] = self.email_subject
        e_msg['X-Act-Checkin'] = self.email_info.project_name
        e_msg['X-Git-Author'] = self.author or self.email_info.email_from
        e_msg['X-Git-Refname'] = self.ref_name
        e_msg['X-Git-Oldrev'] = self.old_rev
        e_msg['X-Git-Newrev'] = self.new_rev

        # email_from = e_msg.get('From')
        email_recipients = [addr[1] for addr
                            in getaddresses(e_msg.get_all('To', [])
                                            + e_msg.get_all('Cc', [])
                                            + e_msg.get_all('Bcc', []))]

        if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
            # Use debug level 0 to make sure that the trace is always
            # printed.
            debug(e_msg.as_string(), level=0)
        else:  # pragma: no cover (do not want real emails during testing)
            sendmail(self.email_info.email_from, email_recipients,
                     e_msg.as_string(), 'localhost')
