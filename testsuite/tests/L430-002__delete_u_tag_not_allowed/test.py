from support import *
import re

class TestRun(TestCase):
    def test_delete_lightweight_tag(self):
        """Try deleting a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :some-tag'.split())
        self.assertNotEqual(p.status, 0, ex_run_image(p))
        self.assertTrue(re.match('.*Deleting a tag is not allowed in '
                                    'this repository',
                                 p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
