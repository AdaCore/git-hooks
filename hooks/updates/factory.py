"""A module providing an AbstractUpdate factory."""
from enum import Enum

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


# The different types of reference updates.
class UpdateKind(Enum):
    # A new reference being created;
    create = 1
    # An existing reference being deleted;
    delete = 2
    # An existing reference being updated (it already existed before,
    # and its value is being changed).
    update = 3


REF_CHANGE_MAP = {
    ('refs/heads/',   UpdateKind.create, 'commit'): BranchCreation,
    ('refs/heads/',   UpdateKind.delete, 'commit'): BranchDeletion,
    ('refs/heads/',   UpdateKind.update, 'commit'): BranchUpdate,
    ('refs/for/',     UpdateKind.create, 'commit'): BranchCreation,
    ('refs/for/',     UpdateKind.delete, 'commit'): BranchDeletion,
    ('refs/for/',     UpdateKind.update, 'commit'): BranchUpdate,
    ('refs/meta/',    UpdateKind.create, 'commit'): BranchCreation,
    ('refs/meta/',    UpdateKind.update, 'commit'): BranchUpdate,
    # Do not allow refs/meta/.* branch deletion for now.
    ('refs/meta/',    UpdateKind.delete, 'commit'): None,
    ('refs/publish/', UpdateKind.create, 'commit'): BranchCreation,
    ('refs/publish/', UpdateKind.delete, 'commit'): BranchDeletion,
    ('refs/publish/', UpdateKind.update, 'commit'): BranchUpdate,
    ('refs/drafts/',  UpdateKind.create, 'commit'): BranchCreation,
    ('refs/drafts/',  UpdateKind.delete, 'commit'): BranchDeletion,
    ('refs/drafts/',  UpdateKind.update, 'commit'): BranchUpdate,
    ('refs/notes/',   UpdateKind.create, 'commit'): NotesCreation,
    ('refs/notes/',   UpdateKind.delete, 'commit'): NotesDeletion,
    ('refs/notes/',   UpdateKind.update, 'commit'): NotesUpdate,
    ('refs/tags/',    UpdateKind.create, 'tag'):    AnnotatedTagCreation,
    ('refs/tags/',    UpdateKind.delete, 'tag'):    AnnotatedTagDeletion,
    ('refs/tags/',    UpdateKind.update, 'tag'):    AnnotatedTagUpdate,
    ('refs/tags/',    UpdateKind.create, 'commit'): LightweightTagCreation,
    ('refs/tags/',    UpdateKind.delete, 'commit'): LightweightTagDeletion,
    ('refs/tags/',    UpdateKind.update, 'commit'): LightweightTagUpdate,
}


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

    new_cls = None
    for key in REF_CHANGE_MAP:
        (map_ref_prefix, map_change_type, map_object_type) = key
        if ((change_type == map_change_type
             and object_type == map_object_type
             and ref_name.startswith(map_ref_prefix))):
            new_cls = REF_CHANGE_MAP[key]
            break
    if new_cls is None:
        return None

    return new_cls(ref_name, old_rev, new_rev, all_refs,
                   submitter_email)
