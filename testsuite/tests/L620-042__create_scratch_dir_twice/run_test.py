from support import *


class TestRun(TestCase):
    def test_git_config(testcase):
        """Unit test git_config with invalid config name..."""
        testcase.run_unit_test_script(
            expected_out="""\
DEBUG: Calling utils.create_scratch_dir (call #1)...
DEBUG: Deleting scratch dir...
DEBUG: Calling utils.create_scratch_dir (call #2)...
       (this call is expected to generate a warning)
*** Unexpected second call to create_scratch_dir
DEBUG: Deleting crash dir again...
"""
        )


if __name__ == "__main__":
    runtests()