"""A module providing an AbstractUpdate factory."""

from git import is_null_rev, get_object_type
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

# The different types of reference updates:
#    - CREATE: The reference is new and has just been created;
#    - DELETE: The reference has just been deleted;
#    - UPDATE: The reference already existed before and its value
#              has just been udpated.
# These constants act as poor-man's enumerations.
(CREATE, DELETE, UPDATE) = range(3)

REF_CHANGE_MAP = {
    ('refs/heads/',        CREATE, 'commit'): BranchCreation,
    ('refs/heads/',        DELETE, 'commit'): BranchDeletion,
    ('refs/heads/',        UPDATE, 'commit'): BranchUpdate,
    ('refs/for/',          CREATE, 'commit'): BranchCreation,
    ('refs/for/',          DELETE, 'commit'): BranchDeletion,
    ('refs/for/',          UPDATE, 'commit'): BranchUpdate,
    ('refs/meta/',         CREATE, 'commit'): BranchCreation,
    ('refs/meta/',         UPDATE, 'commit'): BranchUpdate,
    ('refs/meta/',         DELETE, 'commit'): None,  # Not allowed for now.
    ('refs/publish/',      CREATE, 'commit'): BranchCreation,
    ('refs/publish/',      DELETE, 'commit'): BranchDeletion,
    ('refs/publish/',      UPDATE, 'commit'): BranchUpdate,
    ('refs/drafts/',       CREATE, 'commit'): BranchCreation,
    ('refs/drafts/',       DELETE, 'commit'): BranchDeletion,
    ('refs/drafts/',       UPDATE, 'commit'): BranchUpdate,
    ('refs/notes/commits', CREATE, 'commit'): NotesCreation,
    ('refs/notes/commits', DELETE, 'commit'): NotesDeletion,
    ('refs/notes/commits', UPDATE, 'commit'): NotesUpdate,
    ('refs/tags/',         CREATE, 'tag'):    AnnotatedTagCreation,
    ('refs/tags/',         DELETE, 'tag'):    AnnotatedTagDeletion,
    ('refs/tags/',         UPDATE, 'tag'):    AnnotatedTagUpdate,
    ('refs/tags/',         CREATE, 'commit'): LightweightTagCreation,
    ('refs/tags/',         DELETE, 'commit'): LightweightTagDeletion,
    ('refs/tags/',         UPDATE, 'commit'): LightweightTagUpdate,
}


def new_update(ref_name, old_rev, new_rev, all_refs, submitter_email):
    """Return the correct object for the given parameters.

    PARAMETERS
        See AbstractUpdate.__init__.

    RETURN VALUE
        An object of the correct AbstractUpdate (child) class.
    """
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
