from support import *

class TestRun(TestCase):
    def test_git_config(self):
        """Unit test AbstractRefChange child class missing methods.
        """
        self.enable_unit_test()

        from post_receive import AbstractRefChange
        from utils import InvalidUpdate

        # Define new classes deriving from AbstractRefChange.
        # Normally, that new class is expected to override
        # the following (abstract) methods:
        #   - get_email_subject
        #   - get_email_body
        #
        # The purpose of this test is to verify that an exception
        # is raised if these methods are called in a child class
        # that failed to provide new implementations.

        class NoEmailSubject(AbstractRefChange):
            def get_email_body(self):
                return "email body"

        class NoEmailBody(AbstractRefChange):
            def get_email_subject(self):
                return "email subject"

        with self.assertRaises(InvalidUpdate):
            NoEmailSubject('refs/heads/master',
                           '6ba296bcb2f1781ba928d5c6ae7ebd5a7edecfd7',
                           '77c28ce7c17177486e768595747d37c786a36521',
                           'repo',
                           'someone@example.com',
                           'somewhere@example.com')

        with self.assertRaises(InvalidUpdate):
            NoEmailBody('refs/heads/master',
                        '6ba296bcb2f1781ba928d5c6ae7ebd5a7edecfd7',
                        '77c28ce7c17177486e768595747d37c786a36521',
                        'repo',
                        'someone@example.com',
                        'somewhere@example.com')


if __name__ == '__main__':
    runtests()
