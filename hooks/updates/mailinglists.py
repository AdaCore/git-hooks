"""Handling of the hooks.mailinglist config...
"""
from config import git_config
from io_utils import encode_utf8, safe_decode
import os
from subprocess import Popen, PIPE
from utils import warn


def is_mailinglist_script(name):
    """Return true if the given hooks.mailinglist entry is a script...

    ... rather than an email address.

    PARAMETERS
        name: A string, containing one entry from the hooks.mailinglist
            config.
    """
    # By convention, we identify scripts as being absolute filenames
    # that have enough permissions to execute.
    return os.path.isabs(name) and os.access(name, os.R_OK and os.X_OK)


def get_emails_from_script(script_filename, ref_name, changed_files):
    """The list of emails addresses for the given list of changed files.

    This list is obtained by running the given script, and passing it
    the list of changed files via stdin (one file per line). By
    convention, passing nothing via stdin (no file changed) should
    trigger the script to return all email addresses.

    PARAMETERS
        ref_name: The name of the reference being updated.
        script_filename: The name of the script to execute.
        changed_files: A list of files to pass to the script (via stdin).
            None is also accepted in place of an empty list.
    """
    input_str = "" if changed_files is None else "\n".join(changed_files)

    p = Popen([script_filename, ref_name], stdin=PIPE, stdout=PIPE)
    (output, _) = p.communicate(input=encode_utf8(input_str))
    if p.returncode != 0:
        warn("!!! %s failed with error code: %d." % (script_filename, p.returncode))
    return safe_decode(output).splitlines()


def expanded_mailing_list(ref_name, get_files_changed_cb):
    """Return the list of emails after expanding the hooks.mailinglist config.

    This function iterates over all entries in hooks.mailinglist, and
    replaces all entries which are a script by the result of calling
    that script with the list of changed files.

    PARAMETERS
        ref_name: The name of the reference being updated.
        get_files_changed_cb: A function to call in order to get
            the list of files changed, to be passed to mailinglist
            scripts.  This is a function rather than a list to allow
            us to compute that list of files only if needed.
            None for no file changed.
    """
    result = []
    files_changed = () if get_files_changed_cb is None else None

    for entry in git_config("hooks.mailinglist"):
        if is_mailinglist_script(entry):
            if files_changed is None:
                files_changed = get_files_changed_cb()
            result.extend(get_emails_from_script(entry, ref_name, files_changed))
        else:
            result.append(entry)
    return result
