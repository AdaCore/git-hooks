from support import *
import re

class TestRun(TestCase):
    def test_delete_lightweight_tag(self):
        """Try deleting a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :some-tag'.split())
        self.assertNotEqual(p.status, 0, p.image)
        self.assertTrue(re.match('.*Deleting a tag is not allowed in '
                                    'this repository',
                                 p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
