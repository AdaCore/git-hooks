"""Implements git's post-receive hook.

The arguments for this hook are passed via stdin: For each reference
that is updated, stdin contains one line with 3 space-separated
tokens: the old SHA1, the new SHA1, and the reference name (Eg:
refs/heads/master).
"""
from argparse import ArgumentParser
from collections import OrderedDict
import sys

from config import ThirdPartyHook
from daemon import run_in_daemon
from git import git_show_ref
from init import init_all_globals
from updates.emails import EmailQueue
from updates.factory import new_update
from utils import debug, warn


def post_receive_one(ref_name, old_rev, new_rev, refs, submitter_email):
    """post-receive treatment for one reference.

    PARAMETERS
        ref_name: The name of the reference.
        old_rev: The SHA1 of the reference before the update.
        new_rev: The SHA1 of the reference after the update.
        refs: A dictionary containing all references, as described
            in git_show_ref.
        submitter_email: Same as AbstractUpdate.__init__.
    """
    debug('post_receive_one(ref_name=%s\n'
          '                        old_rev=%s\n'
          '                        new_rev=%s)'
          % (ref_name, old_rev, new_rev))

    update = new_update(ref_name, old_rev, new_rev, refs, submitter_email)
    if update is None:
        # We emit a warning, rather than trigger an assertion, because
        # it gives the script a chance to process any other reference
        # that was updated, but not processed yet.
        warn("post-receive: Unsupported reference update: %s (ignored)."
             % ref_name,
             "              old_rev = %s" % old_rev,
             "              new_rev = %s" % new_rev)
        return
    update.send_email_notifications()


def post_receive(updated_refs, submitter_email):
    """Implement the post-receive hook for all given updated_refs.

    PARAMETERS
        updated_refs: An OrderedDict, indexed by the name of the ref
            being updated, and containing 2-elements tuple.  This tuple
            contains the previous revision, and the new revision of the
            reference.
        submitter_email: Same as AbstractUpdate.__init__.
    """
    refs = git_show_ref()

    for ref_name in updated_refs.keys():
        (old_rev, new_rev) = updated_refs[ref_name]
        post_receive_one(ref_name, old_rev, new_rev, refs,
                         submitter_email)

    # Flush the email queue.  Since this involves creating a daemon,
    # only do so if there is at least one email to be sent.
    email_queue = EmailQueue()
    if email_queue.queue:
        run_in_daemon(email_queue.flush)


def maybe_post_receive_hook(post_receive_data):
    """Call the post-receive-hook is required.

    This function implements supports for the hooks.post-receive-hook
    config variable, by calling this function if the config variable
    is defined.
    """
    result = ThirdPartyHook('hooks.post-receive-hook').call_if_defined(
        hook_input=post_receive_data)
    if result is not None:
        hook_exe, p, out = result
        sys.stdout.write(out)
        # Flush stdout now, to make sure the script's output is printed
        # ahead of the warning below, which is directed to stderr.
        sys.stdout.flush()
        if p.returncode != 0:
            warn('!!! WARNING: %s returned code: %d.'
                 % (hook_exe, p.returncode))


def parse_command_line():
    """Return a namespace built after parsing the command line."""
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    ap = ArgumentParser(description='Git "post-receive" hook.')
    ap.add_argument('--submitter-email',
                    help=('Use this email address as the sender'
                          ' of email notifications instead of using the'
                          ' email address of the user calling this'
                          ' script'))
    return ap.parse_args()


if __name__ == '__main__':
    args = parse_command_line()

    stdin = sys.stdin.read()
    refs_data = OrderedDict()
    for line in stdin.splitlines():
        old_rev, new_rev, ref_name = line.strip().split()
        refs_data[ref_name] = (old_rev, new_rev)

    init_all_globals(refs_data)
    post_receive(refs_data, args.submitter_email)
    maybe_post_receive_hook(stdin)
