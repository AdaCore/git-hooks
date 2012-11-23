"""Implements git's post-receive hook.

The arguments for this hook are passed via stdin: For each reference
that is updated, stdin contains one line with 3 space-separated
tokens: the old SHA1, the new SHA1, and the reference name (Eg:
refs/heads/master).
"""
from argparse import ArgumentParser
from collections import OrderedDict
import re
import sys

from config import git_config
from git import (is_null_rev, get_object_type,
                 commit_oneline, parse_tag_object)
from updates.emails import EmailInfo, Email
from utils import (debug, warn, InvalidUpdate)


class AbstractRefChange(object):
    """Abstract class dealing with reference change.

    The references in question can be any reference, including tags,
    or branches.  The change can be the creation of that reference,
    the deletion of that reference, or the update of that reference.

    ATTRIBUTES
        ref_name: The name of the reference that just got updated.
        old_rev: The reference's old SHA1.
        new_rev: The reference's new SHA1.
        short_ref_name: The name of the reference without the "refs/[...]/"
            prefix.
        email_info: An EmailInfo object.
        email_subject: The subject of the email notification.
        email_body: The body of the email notification.
    """
    def __init__(self, ref_name, old_rev, new_rev, email_info):
        """The constructor.

        PARAMETERS
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
            email_info: Same as the attribute.
        """
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.ref_name = ref_name

        m = re.match(r"refs/[^/]*/(.*)", ref_name)
        self.short_ref_name = m.group(1) if m else ref_name

        self.email_info = email_info
        self.email_subject = self.get_email_subject()
        self.email_body = self.get_email_body()

    def get_email_subject(self):
        """Return the subject of the email to be sent for this change.

        This method must be overridden by the child class, or else
        will raise InvalidUpdate.

        RETURN VALUE
            A string containing the email subject.
        """
        raise InvalidUpdate(
            'Internal error: get_email_subject not implemented')

    def get_email_body(self):
        """Return the body of the email to be sent for this change.

        This method must be overridden by the child class, or else
        will raise InvalidUpdate.

        RETURN VALUE
            A string containing the email subject.
        """
        raise InvalidUpdate(
            'Internal error: get_email_subject not implemented')

    def send_email(self):
        """Send the email notification corresponding to this change.

        REMARKS
            Child classes may override this method if standard
            behavior is not suitable for their type of change.
        """
        email = Email(self.email_info, self.email_subject, self.email_body,
                      self.ref_name, self.old_rev, self.new_rev)
        email.send()


class LightweightTagCreation(AbstractRefChange):
    """An lightweight tag creation...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Created tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        return ("""\
The lightweight tag '%(short_ref_name)s' was created pointing to:

 %(commit_oneline)s"""
                % {'short_ref_name' : self.short_ref_name,
                   'commit_oneline' : commit_oneline(self.new_rev),
                  })


class LightweightTagDeletion(AbstractRefChange):
    """An lightweight tag deletion...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Deleted tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        return ("""\
The lightweight tag '%(short_ref_name)s' was deleted.
It previously pointed to:

 %(commit_oneline)s"""
                % {'short_ref_name' : self.short_ref_name,
                   'commit_oneline' : commit_oneline(self.old_rev),
                  })


class LightweightTagUpdate(AbstractRefChange):
    """An lightweight tag update...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Updated tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        return ("""\
The lightweight tag '%(short_ref_name)s' was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s"""
                % {'short_ref_name' : self.short_ref_name,
                   'commit_oneline' : commit_oneline(self.new_rev),
                   'old_commit_oneline' : commit_oneline(self.old_rev),
                  })


class AnnotatedTagCreation(AbstractRefChange):
    """An annotated tag creation...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Created tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        template = """\
The %(tag_kind)s tag '%(short_ref_name)s' was created pointing to:

 %(commit_oneline)s

Tagger: %(tagger)s
Date: %(date)s

%(message)s"""

        tag_info = parse_tag_object(self.short_ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['short_ref_name'] = self.short_ref_name
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)

        return template % tag_info


class AnnotatedTagDeletion(AbstractRefChange):
    """An annotated tag deletion...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Deleted tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        template = """\
The annotated tag '%(short_ref_name)s' was deleted.
It previously pointed to:

 %(commit_oneline)s"""

        template_data = {}
        template_data['short_ref_name'] = self.short_ref_name
        template_data['commit_oneline'] = commit_oneline(self.old_rev)

        return template % template_data


class AnnotatedTagUpdate(AbstractRefChange):
    """An annotated tag update...
    """
    def get_email_subject(self):
        """See AbstractRefChange.get_email_subject.
        """
        return '[%s] Updated tag %s' % (self.email_info.project_name,
                                        self.short_ref_name)

    def get_email_body(self):
        """See AbstractRefChange.get_email_body.
        """
        template = """\
The %(tag_kind)s tag '%(short_ref_name)s' was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s

Tagger: %(tagger)s
Date: %(date)s

%(message)s"""

        tag_info = parse_tag_object(self.short_ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['short_ref_name'] = self.short_ref_name
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)
        tag_info['old_commit_oneline'] = commit_oneline(self.old_rev)

        return template % tag_info


# The different types of reference updates:
#    - CREATE: The reference is new and has just been created;
#    - DELETE: The reference has just been deleted;
#    - UPDATE: The reference already existed before and its value
#              has just been udpated.
# These constants act as poor-man's enumerations.
(CREATE, DELETE, UPDATE) = range(3)

# A dictionary that maps the type of update to the associated
# concrete RefChange class.
#
# This dictionary is indexed by a tuple with the following entries:
#    [0] The reference name prefix: The name of the reference being
#        updated must start with this prefix;
#    [1] The type of update (one of the CREATE, DELETE, etc, constants
#        above);
#    [2] The object type (usually 'tag' or 'commit').

REF_CHANGE_MAP = {
    ('refs/tags/', CREATE, 'commit') : LightweightTagCreation,
    ('refs/tags/', DELETE, 'commit') : LightweightTagDeletion,
    ('refs/tags/', UPDATE, 'commit') : LightweightTagUpdate,
    ('refs/tags/', CREATE, 'tag')    : AnnotatedTagCreation,
    ('refs/tags/', DELETE, 'tag')    : AnnotatedTagDeletion,
    ('refs/tags/', UPDATE, 'tag')    : AnnotatedTagUpdate,
}


def post_receive_one(ref_name, old_rev, new_rev, email_info):
    """post-receive treatment for one reference.

    PARAMETERS
        ref_name: The name of the reference.
        old_rev: The SHA1 of the reference before the update.
        new_rev: The SHA1 of the reference after the update.
        email_info: An EmailInfo object.
    """
    debug('post_receive_one(ref_name=%s\n'
          '                        old_rev=%s\n'
          '                        new_rev=%s)'
          % (old_rev, new_rev, ref_name))

    # Check the hooks.noemails configuration parameter.  If it exists,
    # it is a comma-separated list of names of ref names for which commits
    # should not trigger an update email.
    no_emails = git_config("hooks.noemails")
    if no_emails and ref_name in no_emails.split(","):
        print "---------------------------------------------------------------"
        print "-- The hooks.noemails config parameter contains `%s'." % ref_name
        print "-- Commit emails will therefore not be sent."
        print "---------------------------------------------------------------"
        return

    # Note: The old version of these scripts were canonicalizing
    # old_rev and new_rev using "git rev-parse".  But, not knowing
    # whether this is really necessary or not, or under which
    # condition it would be necessary, we refrain from doing it
    # here.

    # At least one of the references must be non-null...
    assert not (is_null_rev(old_rev) and is_null_rev(new_rev))

    if is_null_rev(old_rev):
        change_type = CREATE
        object_type = get_object_type(new_rev)
    elif is_null_rev(new_rev):
        change_type = DELETE
        object_type = get_object_type(old_rev)
    else:
        change_type = UPDATE
        object_type = get_object_type(new_rev)

    ref_change_klass = None
    for key in REF_CHANGE_MAP:
        (map_ref_prefix, map_change_type, map_object_type) = key
        if (change_type == map_change_type
            and object_type == map_object_type
            and ref_name.startswith(map_ref_prefix)):
            ref_change_klass = REF_CHANGE_MAP[key]
            break

    if ref_change_klass is None: # pragma: no cover (should be impossible)
        # We emit a warning, rather than trigger an assertion, because
        # it gives the script a chance to process any other reference
        # that was updated, but not processed yet.
        warn("post-receive: Unsupported reference update: %s,%s (ignored)."
             % (ref_name, object_type))
        return

    change = ref_change_klass(ref_name, old_rev, new_rev, email_info)
    change.send_email()


def post_receive(updated_refs):
    """Implement the post-receive hook for all given updated_refs.

    PARAMETERS
        updated_refs: An OrderedDict, indexed by the name of the ref
            being updated, and containing 2-elements tuple.  This tuple
            contains the previous revision, and the new revision of the
            reference.
    """
    email_info = EmailInfo()

    for ref_name in updated_refs.keys():
        (old_rev, new_rev) = updated_refs[ref_name]
        post_receive_one(ref_name, old_rev, new_rev, email_info)


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
    ap.add_argument('old_rev',
                    help='the SHA1 before update')
    ap.add_argument('new_rev',
                    help='the new SHA1, if the update is accepted')
    ap.add_argument('ref_name',
                    help='the name of the reference being updated')

    return ap.parse_args(args)


if __name__ == '__main__':
    refs_data = OrderedDict()
    for line in sys.stdin:
        stdin_argv = line.strip().split()
        args = parse_command_line(stdin_argv)
        refs_data[args.ref_name] = (args.old_rev, args.new_rev)
    try:
        post_receive(refs_data)
    except InvalidUpdate, E:
        warn(*E)

