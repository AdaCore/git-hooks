from support import *
import re

class TestRun(TestCase):
    def test_push_unannotated_tag(self):
        """Try pushing an unnanotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try deleting full-tag.  The remote is setup to refuse this request.
        p = Run('git push origin :full-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))
        self.assertTrue(re.match(r'.*-\s+\[deleted\]\s+full-tag',
                                 p.out, re.DOTALL),
                        ex_run_image(p))


if __name__ == '__main__':
    runtests()
