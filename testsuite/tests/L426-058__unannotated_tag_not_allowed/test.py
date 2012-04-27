from support import *

def has_rejection(out, tag_name):
    if ('Un-annotated tags (%s) are not allowed in this repository' % tag_name
        not in out):
        return False
    if 'error: hook declined to update' not in out:
        return False
    return True

class TestRun(TestCase):
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
