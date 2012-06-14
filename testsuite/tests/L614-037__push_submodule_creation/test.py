from support import *
import os
from os.path import isdir

class TestRun(TestCase):
    def test_push_commit(self):
        """Try pushing a commit that creates a subproject.
        """
        cd ('%s/repo' % TEST_DIR)

        # First, add the submodule...
        p = Run(['git', 'submodule', 'add', '%s/bare/subm.git' % TEST_DIR])
        self.assertTrue(p.status == 0, ex_run_image(p))

        # Verify that subm is a directory that exists...
        self.assertTrue(isdir('subm'),
                        ex_run_image(p) + '\n' + Run(['ls -la'.split()]).out)

        # Now that the setup phase is done, commit the change.
        p = Run(['git', 'commit', '-m', 'Add submodule subm'])
        self.assertTrue(p.status == 0, ex_run_image(p))

        # For coverage purposes, we want to test the calling of
        # the style-check program via the regular method (where
        # GIT_HOOKS_CVS_CHECK is not defined.  But we still want
        # to provide our own.
        #
        # The way we do that is by:
        #   - Provide our own `cvs_check' script in TEST_DIR.
        #   - add TEST_DIR to the front of the PATH.
        #   - Unset GIT_HOOKS_CVS_CHECK.
        #
        # The hooks should see that there is no GIT_HOOKS_CVS_CHECK,
        # and thus call `cvs_check', find our copy from the TEST_DIR
        # that we just added to the front of the PATH, and execute it.
        del os.environ['GIT_HOOKS_CVS_CHECK']
        os.environ['PATH'] = TEST_DIR + ':' + os.environ['PATH']

        # And finally, try pushing that commit.
        # For verification purposes, we enable tracing to level 2,
        # in order to get the one that says that submodule entries
        # are ignored.
        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = '2'
        p = Run('git push origin master'.split())
        self.assertTrue(p.status == 0, ex_run_image(p))

        self.assertTrue('DEBUG: subproject entry ignored: subm' in p.out,
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
