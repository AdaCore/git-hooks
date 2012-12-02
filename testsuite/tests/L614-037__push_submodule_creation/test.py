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
        self.assertTrue(p.status == 0, p.image)

        # Verify that subm is a directory that exists...
        self.assertTrue(isdir('subm'),
                        p.image + '\n' + Run(['ls -la'.split()]).cmd_out)

        # Now that the setup phase is done, commit the change.
        p = Run(['git', 'commit', '-m', 'Add submodule subm'])
        self.assertTrue(p.status == 0, p.image)

        # Get the hash of our submodule commit.  We will need it
        # to match the output of the push command.
        p = Run(['git rev-parse HEAD'.split()])
        self.assertTrue(p.status == 0, p.image)
        subm_rev = p.out.strip()

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
        self.set_debug_level(2)
        p = Run('git push origin master'.split())
        expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=7a373b536b65b600a449b5c739c137301f6fd364, new_rev=%(subm_rev)s)
remote: DEBUG: validate_ref_update (refs/heads/master, 7a373b536b65b600a449b5c739c137301f6fd364, %(subm_rev)s)
remote: DEBUG: update base: 7a373b536b65b600a449b5c739c137301f6fd364
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=7a373b536b65b600a449b5c739c137301f6fd364, new_rev=%(subm_rev)s)
remote: *** cvs_check: `trunk/repo/.gitmodules'
remote:   DEBUG: subproject entry ignored: subm
remote: DEBUG: post_receive_one(ref_name=7a373b536b65b600a449b5c739c137301f6fd364
remote:                         old_rev=%(subm_rev)s
remote:                         new_rev=refs/heads/master)
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   7a373b5..%(short_subm_rev)s  master -> master
""" % {'subm_rev' : subm_rev,
       'short_subm_rev' : subm_rev[0:7]}

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
