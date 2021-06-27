from support import TestCase, runtests


class TestRun(TestCase):
    def test_failure(testcase):
        """A (non-)test that should fail."""
        testcase.assertEqual(True, False)


if __name__ == "__main__":
    runtests()
