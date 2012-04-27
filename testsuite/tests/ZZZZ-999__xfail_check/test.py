from support import TestCase, runtests

class TestRun(TestCase):
    def test_failure(self):
        """A (non-)test that should fail.
        """
        self.assertEqual(True, False)

if __name__ == '__main__':
    runtests()
