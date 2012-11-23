from support import *

class TestRun(TestCase):
    def test_check_update(self):
        """Unit test update.check_update.
        """
        self.enable_unit_test()

        from update import check_update
        from utils import InvalidUpdate

        with self.assertRaisesRegexp(
            InvalidUpdate,
            r'This type of update \(some/dummy_refname,commit\) is '
                'currently unsupported\.'):
            check_update('some/dummy_refname',
                         '8ef2d60c830f70e70268ce886209805f5010db1f',
                         'd065089ff184d97934c010ccd0e7e8ed94cb7165')


if __name__ == '__main__':
    runtests()
