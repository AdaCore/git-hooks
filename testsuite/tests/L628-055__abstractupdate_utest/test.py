from support import *

class TestRun(TestCase):
    def test_git_config(self):
        """Unit test AbstractUpdate child class missing methods.
        """
        self.enable_unit_test()

        # Define new classes deriving from AbstractRefChange.
        # Normally, that new class is expected to override
        # a certain number of methods.  The purpose of this test
        # is to # verify that an exception is raised if these methods
        # are called in a child class that failed to provide new
        # implementations.

        from updates import AbstractUpdate

        class MissingSelfSanityCheck(AbstractUpdate):
            pass

        class MissingOtherMethods(AbstractUpdate):
            def self_sanity_check(self):
                pass

        with self.assertRaises(AssertionError):
            MissingSelfSanityCheck(
                'refs/heads/master',
                '0000000000000000000000000000000000000000',
                'd065089ff184d97934c010ccd0e7e8ed94cb7165',
                None)

        bad_update = MissingOtherMethods(
            'refs/heads/master',
            '0000000000000000000000000000000000000000',
            'd065089ff184d97934c010ccd0e7e8ed94cb7165',
            None)

        with self.assertRaises(AssertionError):
            bad_update.validate_ref_update()

        with self.assertRaises(AssertionError):
            # No need to pass a valid EmailInfo, pass None instead.
            bad_update.get_update_email_contents(None)


if __name__ == '__main__':
    runtests()
