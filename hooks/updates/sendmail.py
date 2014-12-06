"""A module to send emails...
"""
from gnatpython.ex import Run

import os


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
    for sendmail in ('/usr/lib/sendmail', '/usr/sbin/sendmail'):
        if os.path.exists(sendmail):
            p = Run([sendmail] + to_emails, input="|" +
                    mail_as_string, output=None)
            return p.status == 0

    # Else try to use smtplib
    import smtplib
    s = smtplib.SMTP(smtp_server)
    s.sendmail(from_email, to_emails, mail_as_string)
    s.quit()
    return True
