from updates.sendmail import get_sendmail_exe


def check_minimum_system_requirements():
    """Raise InvalidUpdate if some minimum requirements are missing."""
    get_sendmail_exe()
