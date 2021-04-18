"""A module to send emails...
"""
from __future__ import print_function
import os
from subprocess import Popen, PIPE, STDOUT


def sendmail(from_email, to_emails, mail_as_string, smtp_server):
    """Send an email with sendmail or stmplib

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
    for sendmail in ("/usr/lib/sendmail", "/usr/sbin/sendmail"):
        if os.path.exists(sendmail):
            p = Popen([sendmail] + to_emails, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            out, _ = p.communicate(mail_as_string)
            if p.returncode != 0:
                print(out)
            return p.returncode == 0

    # Else try using smtplib
    import smtplib

    s = smtplib.SMTP(smtp_server)
    s.sendmail(from_email, to_emails, mail_as_string)
    s.quit()
    return True
