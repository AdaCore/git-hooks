"""Implements git's post-receive hook.

The arguments for this hook are passed via stdin: For each reference
that is updated, stdin contains one line with 3 space-separated
tokens: the old SHA1, the new SHA1, and the reference name (Eg:
refs/heads/master).
"""
from argparse import ArgumentParser
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT
import sys

from config import git_config
from daemon import run_in_daemon
from git import git_show_ref
from updates.emails import EmailQueue
from updates.factory import new_update
from utils import (debug, warn)


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
    hook_exe = git_config('hooks.post-receive-hook')
    if hook_exe is None:
        return
    p = Popen([hook_exe], stdin=PIPE, stdout=sys.stdout, stderr=STDOUT)
    p.communicate(post_receive_data)
    if p.returncode != 0:
        warn('!!! WARNING: %s returned code: %d.' % (hook_exe, p.returncode))


def parse_command_line(args):
    """Return a namespace built after parsing the command line.

    PARAMETERS
        args: A sequence of arguments to be used as the command-line.
    """
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    #
    # We use ArgumentParser, which means that we are requiring
    # Python version 2.7 or later, because it handles mandatory
    # command-line arguments for us as well.
    ap = ArgumentParser(description='Git "update" hook.')
    ap.add_argument('--submitter-email',
                    help=('Use this email address instead as the sender'
                          ' of email notifications instead of using the'
                          ' email address of the user calling this'
                          ' script'))
    ap.add_argument('old_rev',
                    help='the SHA1 before update')
    ap.add_argument('new_rev',
                    help='the new SHA1, if the update is accepted')
    ap.add_argument('ref_name',
                    help='the name of the reference being updated')

    return ap.parse_args(args)


if __name__ == '__main__':
    stdin = sys.stdin.read()
    refs_data = OrderedDict()
    for line in stdin.splitlines():
        stdin_argv = line.strip().split() + sys.argv[1:]
        args = parse_command_line(stdin_argv)
        refs_data[args.ref_name] = (args.old_rev, args.new_rev)
    post_receive(refs_data, args.submitter_email)
    maybe_post_receive_hook(stdin)
