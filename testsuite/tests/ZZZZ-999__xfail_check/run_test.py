import pytest


@pytest.mark.xfail(reason="testcase always expected to fail (helps check framework)")
def test_failure(testcase):
    """A (non-)test that should fail."""
    testcase.assertEqual(True, False)
