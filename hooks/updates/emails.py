"""Email helpers for sending update-related emails."""

from config import git_config
from email.charset import Charset, QP
from email.header import Header
from email.mime.text import MIMEText
from email.utils import getaddresses, parseaddr
from errors import InvalidUpdate
from git import get_module_name
from io_utils import encode_utf8, safe_decode
import os
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from updates.sendmail import sendmail
from utils import debug, get_user_name, get_user_full_name

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

        from_domain = git_config("hooks.from-domain")
        if not from_domain:
            raise InvalidUpdate(
                "Error: hooks.from-domain config variable not set.",
                "Please contact your repository's administrator.",
            )
        if email_from is None:
            self.email_from = "%s <%s@%s>" % (
                get_user_full_name(),
                get_user_name(),
                from_domain,
            )
        else:
            self.email_from = email_from


class EmailQueue(object):
    """An email queue (a singleton).

    ATTRIBUTES
        queue: A list of emails to be sent.
    """

    def __new__(cls, *args, **kw):
        """The allocator."""
        if not hasattr(cls, "_instance"):
            orig = super(EmailQueue, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        """The constructor."""
        # If the singleton has never been initialized, do it now.
        if not hasattr(self, "queue"):
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
                if "GIT_HOOKS_TESTSUITE_MODE" in os.environ:
                    # For the testsuite, print a debug trace in place
                    # of delaying the execution.  Use debug level 0
                    # to make sure it is always printed (to make sure
                    # the testsuite always alerts us if there is any
                    # change in the delay policy).
                    debug("inter-email delay...", level=0)
                else:  # pragma: no cover (do not want delays during testing)
                    sleep(EMAIL_DELAY_IN_SECONDS)
        self.queue = []


class EmailCustomContents(object):
    """An object used to describe email customizations.

    This class is mostly a convenience class to store various
    attributes, and objects of this class are only really meaningful
    in conjunction with an Email object, as the attributes describe
    how certain parts of the email are to be adapted.

    ATTRIBUTES
        subject: If not None, the new email subject.
        body: If not None, the new email body (not including the "Diff:"
            section.
        appendix: If not None, some additional text to be added at
            the end of the email's body.
        diff: The contents of the "Diff:" section. If None, the "Diff:"
            section is omitted.
    """

    def __init__(self, subject=None, body=None, appendix=None, diff=None):
        """Initialize an EmailCustomContents object.

        PARAMETERS
            subject: Same as the attribute.
            body: Same as the attribute.
            appendix: Same as the attribute.
            diff: Same as the attribute.
        """
        self.subject = subject
        self.body = body
        self.appendix = appendix
        self.diff = diff


class Email(object):
    """An email object.

    All emails to be sent by the git-hooks should be sent via
    this class to ensure consistency.

    ATTRIBUTES
        email_info: An EmailInfo object.
        email_to: A list of email addresses, in RFC 822 format,
            whom to send this email to.
        email_bcc: An iterable of email addresses, in RFC 822 format,
            whom to Bcc this email on. None indicates no Bcc needed.
        email_subject: The email's subject.
        email_body: The email's body, NOT including the diff.
        diff: A diff to be included at the end of the email being
            sent out.
        filer_cmd: If not None, sending this email also results
            in this command being called with the contents of the
            email_body parameter (and therefore, no diff).
        author: A string in "name <email>" format, to be used as
            the X-Git-Author field in the email header. May be None,
            in which case we'll use email_info.email_from instead.
        ref_name: See AbstractUpdate.ref_name attribute.
        old_rev: See AbstractUpdate.old_rev attribute.
        new_rev: See AbstractUpdate.new_rev attribute.
    """

    def __init__(
        self,
        email_info,
        email_to,
        email_bcc,
        email_subject,
        email_body,
        author,
        ref_name,
        old_rev,
        new_rev,
        diff=None,
        filer_cmd=None,
    ):
        """The constructor.

        PARAMETERS
            email_info: Same as the attribute.
            email_to: Same as the attribute.
            email_bcc: Same as the attribute.
            email_subject: Same as the attribute.
            email_body: Same as the attribute.
            author: Same as the attribute.
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
            diff: A diff string, if applicable.  Otherwise None.
                When not None, the diff is appended at the end
                of the email's body - truncated if necessary.
        """
        self.email_info = email_info
        self.email_to = email_to
        self.email_bcc = email_bcc
        self.email_subject = email_subject
        self.email_body = email_body
        self.diff = diff
        self.filer_cmd = filer_cmd
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
        """Perform all send operations related to this email...

        These consists in:
            - send the notification email;
            - call self.filer_cmd if not None.

        REMARKS
            If the GIT_HOOKS_TESTSUITE_MODE environment variable
            is set, then a trace of the email is printed, instead
            of sending it.  This is for testing purposes.
        """
        # Force the charset being used to UTF-8. We could possibly try
        # to guess whether more primitive charsets might work such as
        # ASCII or IS0-8859-15, but UTF-8 is so close to those encodings
        # that it is not worth the extra complication.
        #
        # The one situation where it might be worth guessing the charset
        # is when the email body contains some characters which are not
        # available in UTF-8. Since UTF-8 is so widely used, we'll assume
        # for now that it's not necessary in practice to support this
        # scenario.
        e_msg_charset = Charset("UTF-8")

        # Force quoted-printable encoding for our emails.
        #
        # Using this encoding helps ensure that the email payload
        # does not exceed any of the limitations that SMTP servers
        # might have. In particular, while RFC 6152 now defines
        # the "8bit" Content-Transfer-Encoding as being a legal
        # extension, it also warns us of some limitations:
        #
        #        | Note that this extension does NOT eliminate
        #        | the possibility of an SMTP server limiting line
        #        | length; servers are free to implement this extension
        #        | but nevertheless set a line length limit no lower
        #        | than 1000 octets.
        #
        # We also prefer the quoted-printable encoding over the base64
        # one because:
        #
        #    - The output that's generally easier for humans to read';
        #    - The output is also usually smaller in size for typical
        #      text.
        e_msg_charset.body_encoding = QP

        e_msg_body = self.__email_body_with_diff

        e_msg = MIMEText(e_msg_body, _charset=e_msg_charset)

        # Create the email's header.
        e_msg["From"] = sanitized_email_address(self.email_info.email_from)
        e_msg["To"] = ", ".join(map(sanitized_email_address, self.email_to))
        if self.email_bcc:
            e_msg["Bcc"] = ", ".join(map(sanitized_email_address, self.email_bcc))
        e_msg["Subject"] = sanitized_email_header_field(self.email_subject)
        e_msg["X-Act-Checkin"] = self.email_info.project_name
        e_msg["X-Git-Author"] = sanitized_email_address(
            self.author or self.email_info.email_from
        )
        e_msg["X-Git-Refname"] = self.ref_name
        e_msg["X-Git-Oldrev"] = self.old_rev
        e_msg["X-Git-Newrev"] = self.new_rev

        # email_from = e_msg.get('From')
        email_recipients = [
            addr[1]
            for addr in getaddresses(
                e_msg.get_all("To", [])
                + e_msg.get_all("Cc", [])
                + e_msg.get_all("Bcc", [])
            )
        ]

        sendmail(
            self.email_info.email_from,
            email_recipients,
            e_msg.as_string(),
            "localhost",
        )

        if self.filer_cmd is not None:
            self.__call_filer_cmd()

    @property
    def __email_body_with_diff(self):
        """Return self.email_body with the diff at the end (if any).

        This attributes returns self.email_body augmentted with
        self.diff (if not None), possibly truncated to fit the
        hooks.max-email-diff-size limit, with a "diff marker"
        between email_body and diff.  The diff marker is meant
        to be used by scripts processing the contents of those
        emails but not wanting to include the diff as part of
        their processing.
        """
        email_body = self.email_body
        if self.diff is not None:
            # Append the "Diff:" marker to email_body, followed by
            # the diff. Truncate the patch if necessary.
            diff = self.diff

            max_diff_size = git_config("hooks.max-email-diff-size")
            if len(diff) > max_diff_size:
                diff = diff[:max_diff_size]
                diff += "[...]\n\n[diff truncated at %d bytes]\n" % max_diff_size

            email_body += "\nDiff:\n"
            email_body += diff
        return email_body

    def __call_filer_cmd(self):
        """Call self.filer_cmd to get self.email_body filed.

        The contents that gets filed is a slightly augmented version
        of self.email to provide a little context of what's being
        changed.

        Prints a message on stdout in case of error returned during
        the call.
        """
        ref_name = self.ref_name
        if ref_name.startswith("refs/heads/"):
            # Replace the reference name by something a little more
            # intelligible for normal users.
            ref_name = "The %s branch" % ref_name[11:]
        to_be_filed = (
            "%s has been updated by %s:" % (ref_name, self.email_info.email_from)
            + "\n\n"
            + self.email_body
        )

        p = Popen(self.filer_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out, _ = p.communicate(encode_utf8(to_be_filed))
        if p.returncode != 0:
            print(safe_decode(out))


def guess_encoding(text):
    """Try to guess the given string's encoding.

    The guessing is done by simply trying the more popular encodings
    against the given text.

    PARAMETERS
        text: The string whose encoding we are trying to guess.

    RETURN VALUE
        The name of the encoding (e.g. 'ascii', or 'UTF-8') if that
        encoding is able to decode the given string. None otherwise.
    """
    # Test the more popular encodings, starting with the smaller
    # charsets first.
    for potential_encoding in ("ascii", "UTF-8"):
        try:
            text.encode(potential_encoding)
            return potential_encoding
        except Exception:
            pass


def sanitized_email_header_field(field_body):
    """Return an RFC2047-encoded version of field_body (if necessary)

    If field_body contains characters that are not printable ASCII,
    return an RFC2047-encoded version of this string.  Otherwise,
    that string untouched.

    PARAMETERS
        field_body: A string, to be used as the value of a field
            in an email's header.
    """
    encoding = guess_encoding(field_body)
    if encoding == "ascii" and not any(
        c for c in field_body if ord(c) < 32 or ord(c) > 126
    ):
        # The field body has only ASCII characters in the range 32-126.
        # So no encoding required.
        return field_body

    if encoding is None:  # pragma: no cover (see explanation below)
        # Should never happen, since guess_encoding tries the iso-8859-15
        # encoding which apparently accepts any byte stream.
        # Nevertheless, just in case, do the best we can in that situation,
        # and just send the header as is.
        return field_body

    return Header(field_body, encoding).encode()


def sanitized_email_address(email_address):
    """Return an RFC2047-encoded version of the email_address (if necessary)

    This function splits the email_address into a (gecos, email_spec)
    tuple, and then RFC2047-encodes the gecos portion of the email
    when necessary (using sanitized_email_header_field).  The sanitized
    version of the email address (gecos + email_spec) is then returned.

    PARAMETERS
        email_address: A string containing an email address.
    """
    email_address = email_address.strip()
    gecos, email_spec = parseaddr(email_address)
    if not gecos:
        # There is no GECOS, so the email address is made of only
        # the email-spec portion, which should not require any encoding.
        # So return the email_address as is.
        return email_address
    if not email_spec:  # pragma: no cover (see below)
        # Does not seem to be possible, because (1) Git seems to verify
        # the format of all email addresses before accepting them; and
        # (2) even when feeding an invalid email address such as
        # "invalid <inv', parseaddr above still returns an email_spec.
        # But be robust, just in case, and return the email_address
        # untouched if parseaddr ever returns no email_spec... That's
        # probably the best we can do.
        return email_address

    return "%s <%s>" % (sanitized_email_header_field(gecos), email_spec)
