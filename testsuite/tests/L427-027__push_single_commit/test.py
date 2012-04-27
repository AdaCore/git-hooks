from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)
        p = Run('git push origin master'.split())
        # FIXME: We know this testcase is exercising a feature that
        # is not implemented yet.  When it is, remove the "False"
        # and replace it by a check of the command output.
        self.assertTrue(p.status == 0 and False,
                        ex_run_image(p))

    def test_push_unannotated_tag(self):
        """Try pushing an unnanotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Create a tag called 'new-tag'...
        p = Run('git tag new-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        # Try pushing that new-tag.  The repository has been configured
        # to reject such updates.
        p = Run('git push origin new-tag'.split())
        self.assertTrue(p.status != 0 and has_rejection(p.out, 'new-tag'),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
