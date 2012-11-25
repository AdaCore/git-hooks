from support import *
import re

class TestRun(TestCase):
    def test_push_lightweight_tag(self):
        """Try pushing a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Try deleting full-tag.  The remote is setup to refuse this request.
        p = Run('git push origin :full-tag'.split())
        self.assertNotEqual(p.status, 0, p.image)
        self.assertTrue(re.match('.*Deleting a tag is not allowed in '
                                    'this repository',
                                 p.cmd_out, re.DOTALL),
                        p.image)


if __name__ == '__main__':
    runtests()
