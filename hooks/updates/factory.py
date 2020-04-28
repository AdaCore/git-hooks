"""A module providing an AbstractUpdate factory."""
from collections import namedtuple
from enum import Enum
import re

from config import git_config
from git import is_null_rev, get_object_type
from errors import InvalidUpdate
from updates.branches.creation import BranchCreation
from updates.branches.deletion import BranchDeletion
from updates.branches.update import BranchUpdate
from updates.notes.creation import NotesCreation
from updates.notes.deletion import NotesDeletion
from updates.notes.update import NotesUpdate
from updates.tags.atag_creation import AnnotatedTagCreation
from updates.tags.atag_update import AnnotatedTagUpdate
from updates.tags.atag_deletion import AnnotatedTagDeletion
from updates.tags.ltag_creation import LightweightTagCreation
from updates.tags.ltag_update import LightweightTagUpdate
from updates.tags.ltag_deletion import LightweightTagDeletion


# The different kinds of references we handle.
#
# Note: We try to list the entries in order of frequency, with more
# frequent updates first. That way, anytime some code iterates over
# this enum, it'll get the more frequent update first.
class RefKind(Enum):
    # A branch. The vast majority of updates will be branch updates.
    branch_ref = 1
    # A special branch used to hold git notes.
    notes_ref = 2
    # A tag reference (either annotated or lightweight).
    tag_ref = 3


# The different types of reference updates.
class UpdateKind(Enum):
    # A new reference being created;
    create = 1
    # An existing reference being deleted;
    delete = 2
    # An existing reference being updated (it already existed before,
    # and its value is being changed).
    update = 3


# A named tuple used to determine a repository's namespace information
# for a given kind of reference (RefKind).
NamespaceKey = namedtuple('NamespaceKey', [
    # The name of the config option to use in order to retrieve,
    # for the associated RefKind, the repository's namespace.
    # Should be None if alternate (non-standard) namespaces are not
    # supported for the associated kind of reference.
    'opt_name',
    # The name of the option to use to decide whether the namespaces,
    # which are normally standard for the associated kind of reference,
    # should be used or not.
    # Should be None if alternate (non-standard) namespaces are not
    # supported for this kind of reference.
    'use_std_opt_name',
    # The standard namespaces for that kind of reference:
    # A tuple of strings, each being a regular expression, matching
    # references which are recognized, by default, as this RefKind.
    'std'])

# A dictionary providing namespace information for each kind of reference.
#
# The dictionary is architected as follow:
#   + The key is a RefKind enum;
#   + The value is a NamespaceKey.
NAMESPACES_INFO = {
    RefKind.branch_ref: NamespaceKey(
        opt_name='hooks.branch-ref-namespace',
        use_std_opt_name='hooks.use-standard-branch-ref-namespace',
        std=('refs/heads/.*',    # Git/Gerrit branches.
             'refs/meta/.*',     # Git/Gerrit/git-hooks configuration.
             'refs/drafts/.*',   # Gerrit branches.
             'refs/for/.*',      # Gerrit branches.
             'refs/publish/.*',  # Gerrit branches.
             ),
    ),
    RefKind.notes_ref: NamespaceKey(
        opt_name=None,          # No alternate namespace support.
        use_std_opt_name=None,  # No alternate namespace support.
        std=('refs/notes/.*',
             ),
    ),
    RefKind.tag_ref: NamespaceKey(
        opt_name='hooks.tag-ref-namespace',
        use_std_opt_name='hooks.use-standard-tag-ref-namespace',
        std=('refs/tags/.*',
             ),
    ),
}

REF_CHANGE_MAP = {
    (RefKind.branch_ref, UpdateKind.create, 'commit'): BranchCreation,
    (RefKind.branch_ref, UpdateKind.delete, 'commit'): BranchDeletion,
    (RefKind.branch_ref, UpdateKind.update, 'commit'): BranchUpdate,
    (RefKind.notes_ref,  UpdateKind.create, 'commit'): NotesCreation,
    (RefKind.notes_ref,  UpdateKind.delete, 'commit'): NotesDeletion,
    (RefKind.notes_ref,  UpdateKind.update, 'commit'): NotesUpdate,
    (RefKind.tag_ref,    UpdateKind.create, 'tag'):    AnnotatedTagCreation,
    (RefKind.tag_ref,    UpdateKind.delete, 'tag'):    AnnotatedTagDeletion,
    (RefKind.tag_ref,    UpdateKind.update, 'tag'):    AnnotatedTagUpdate,
    (RefKind.tag_ref,    UpdateKind.create, 'commit'): LightweightTagCreation,
    (RefKind.tag_ref,    UpdateKind.delete, 'commit'): LightweightTagDeletion,
    (RefKind.tag_ref,    UpdateKind.update, 'commit'): LightweightTagUpdate,
}


def get_namespace_info(ref_kind):
    """Return the repository's namespace info for the given type of reference.

    PARAMETERS
        ref_kind: A RefKind object, indicating which kind of reference
            we want the namespace information for.

    RETURN VALUE
        A list of regular expressions, matching the references which
        are recognized by the repository as a reference of the kind
        that was given as ref_kind.
    """
    namespace_info = []

    namespace_key = NAMESPACES_INFO[ref_kind]

    if namespace_key.use_std_opt_name is None or \
            git_config(namespace_key.use_std_opt_name):
        namespace_info.extend(namespace_key.std)

    if namespace_key.opt_name is not None:
        namespace_info.extend(git_config(namespace_key.opt_name))

    return namespace_info


def ref_matches_namespace_pattern(ref_name, namespace_re):
    """Return true iff a reference's name mactches the given namespace pattern.

    PARAMETERS
        ref_name: The name of the reference we want to match against
            namespace_re.
        namespace_re: A regular expression.

    RETURN VALUE
        True if ref_name matches namespace_re. False otherwise.
    """
    m = re.match(namespace_re, ref_name)
    if m is None:
        return False
    # We also need to verify that the namespace pattern matches
    # the whole reference name (i.e. we do not want a reference
    # named 'refs/heads/master2' be considered part of a namespace
    # whose regexp is 'refs/heads/master').
    #
    # With Python 2.7, the simplest is to just verify the extent
    # of the string being matched. Once we transition to Python 3,
    # we can simplify this by using re.fullmatch instead of re.match.
    return m.end() - m.start() == len(ref_name)


def get_ref_kind(ref_name):
    """Return the kind of reference ref_name is (None if unrecognized).

    PARAMETERS
        ref_name: The name of the reference we want to identify via
            matching against the repository's various namespaces.

    RETURN VALUE
        The kind of reference ref_name corresponds to (a RefKind object).
        None if we couldn't identify the kind of reference.
    """
    # Try to determine which kind of reference we are dealing with,
    # by matching the reference name to the declared namespaces
    # of each reference kind.
    #
    # Normally, the repository should be configured in such a way
    # that it doesn't matter which type of reference we test first.
    # However, iterating over the order that the different kinds
    # are declared in class RefKind has a couple of advantages:
    #   - the iteration order is consistent (compared to iterating
    #     over NAMESPACES_INFO's keys, for instance);
    #   - the iteration order follows the order specified in
    #     class RefKind, where the most likely kinds of updates
    #     are listed first (very minor optimization, but comes
    #     pretty much for free).
    for ref_kind in RefKind:
        namespace_info = get_namespace_info(ref_kind)
        for ref_re in namespace_info:
            if ref_matches_namespace_pattern(ref_name, ref_re):
                return ref_kind

    return None


def raise_unrecognized_ref_name(ref_name):
    """Raise InvalidUpdate explaining ref_name is not a recognized reference.

    While at it, try to be helpful to the user by providing,
    in the error message, the repository's actual namespace.

    PARAMETERS
        ref_name: The name of the reference we did not recognize.
    """
    err = ['Unable to determine the type of reference for: {}'
           .format(ref_name),
           '',
           'This repository currently recognizes the following types',
           'of references:',
           ]
    for ref_kind in RefKind:
        err.append('')
        err.append(' * {}:'.format({RefKind.branch_ref: 'Branches',
                                    RefKind.notes_ref: 'Git Notes',
                                    RefKind.tag_ref: 'Tags',
                                    }[ref_kind]))
        err.extend(['      {}'.format(ref_re)
                    for ref_re in get_namespace_info(ref_kind)])
    raise InvalidUpdate(*err)


def new_update(ref_name, old_rev, new_rev, all_refs, submitter_email):
    """Return the correct object for the given parameters.

    PARAMETERS
        See AbstractUpdate.__init__.

    RETURN VALUE
        An object of the correct AbstractUpdate (child) class.
    """
    if is_null_rev(old_rev) and is_null_rev(new_rev):
        # This happens when the user is trying to delete a specific
        # reference which does not exist in the repository.
        #
        # Note that this seems to only happen when the user passes
        # the full reference name in the delete-push. When using
        # a branch name (i.e. 'master' instead of 'refs/heads/master'),
        # git itself notices that the branch doesn't exist and returns
        # an error even before calling the hooks for validation.
        raise InvalidUpdate("unable to delete '{}': remote ref does not exist"
                            .format(ref_name))

    if is_null_rev(old_rev):
        change_type = UpdateKind.create
        object_type = get_object_type(new_rev)
    elif is_null_rev(new_rev):
        change_type = UpdateKind.delete
        object_type = get_object_type(old_rev)
    else:
        change_type = UpdateKind.update
        object_type = get_object_type(new_rev)

    ref_kind = get_ref_kind(ref_name)
    if ref_kind is None:
        raise_unrecognized_ref_name(ref_name)

    new_cls = REF_CHANGE_MAP.get((ref_kind, change_type, object_type), None)
    if new_cls is None:
        return None

    return new_cls(ref_name, old_rev, new_rev, all_refs,
                   submitter_email)
