"""The updates root module."""

from git import get_object_type
from utils import debug

class AbstractUpdate(object):
    """An abstract class representing a reference update.

    ATTRIBUTES
        ref_name: The name of the reference being updated.
        short_ref_name: The reference's short name.  It is obtained by
            stripping any character up to, and including, the second
            slash ('/') characater.
            For example, if ref_name is "refs/heads/master", then
            short_ref_name is "master".
        old_rev: The reference's revision (SHA1) prior to the update.
            A null revision means that this is a new reference.
        new_rev: The reference's revision (SHA1) after the update.
            A null revision means that this reference is being deleted.
        new_rev_type: The type of commit that new_rev points to.
            See git.get_object_type for more info.

    REMARKS
        This class is meant to be abstract and should never be instantiated.
    """
    def __init__(self, ref_name, old_rev, new_rev):
        """The constructor.

        Also calls self.auto_sanity_check() at the end.

        PARAMETERS
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
        """
        self.ref_name = ref_name
        self.short_ref_name = ref_name.split('/', 2)[2]
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.new_rev_type = get_object_type(self.new_rev)
        self.self_sanity_check()

    def validate(self):
        """Raise InvalidUpdate if the update is invalid.

        This method verifies that the reference update itself is valid
        (by calling the validate_ref_update method), and then verifies
        that all the new commits introduced by this update passes
        style-checking.  Otherwise, raise InvalidUpdate.
        """
        debug('validate_ref_update (%s, %s, %s)'
              % (self.ref_name, self.old_rev, self.new_rev))
        self.validate_ref_update()

    #------------------------------------------------------------------
    #--  Abstract methods that must be overridden by child classes.  --
    #------------------------------------------------------------------

    def self_sanity_check(self):
        """raise an assertion failure if the init parameters are invalid...

        This method should check that the valud of the attributes created
        at initialization time correspond to values expected for the
        class.  For instance, a class that handles branch creation only
        should verify that the ref_name starts with 'refs/heads/' and
        that old_rev is null.

        REMARKS
            This method is abstract and should be overridden.
        """
        assert False

    def validate_ref_update(self):
        """Raise InvalidUpdate if the update is invalid.

        REMARKS
            This method is abstract and should be overridden.
        """
        assert False

