from support import *
import re

class TestRun(TestCase):
    def test_push_unannotated_tag(self):
        """Try pushing an unnanotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Create a tag called 'new-tag'...
        p = Run('git tag new-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        # Try pushing that new-tag.  The repository has been configured
        # to accept such updates.
        p = Run('git push origin new-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))
        self.assertTrue(re.match(r'.*\[new tag\]\s+new-tag\s+->\s+new-tag\s*$',
                                 p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
