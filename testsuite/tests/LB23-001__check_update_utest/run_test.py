from support import *


class TestRun(TestCase):
    def test_check_update(testcase):
        """Unit test update.check_update."""
        p = testcase.run_unit_test_script(
            expected_out="""\
Unable to determine the type of reference for: some/dummy_refname

This repository currently recognizes the following types
of references:

 * Branches:
      refs/heads/.*
      refs/meta/.*
      refs/drafts/.*
      refs/for/.*
      refs/publish/.*

 * Git Notes:
      refs/notes/.*

 * Tags:
      refs/tags/.*
"""
        )


if __name__ == "__main__":
    runtests()
