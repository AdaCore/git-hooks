"""Management of git references in a git repository.
"""
from git import git_show_ref, is_null_rev


class GitReferences(object):
    """A class to manipulate a "list" of references and their values.

    ATTRIBUTES
        refs: A dictionary, as described in git_show_ref.
    """
    def __init__(self, *args, **kwargs):
        """The constructor.

        PARAMETERS
            All parameters except self are passed as is to git_show_ref,
            and the result is used to set the self.refs attribute.
        """
        self.refs = git_show_ref(*args, **kwargs)

    def update_ref(self, ref_name, new_rev):
        """Update ref_name's value.

        PARAMETERS
            ref_name: The name of the reference to update.
            new_rev: The reference's new value (a null value means that
                the reference is being removed, and thus will result
                in the associated entry to be removed as well).
        """
        if is_null_rev(new_rev):
            del(self.refs[ref_name])
        else:
            self.refs[ref_name] = new_rev
