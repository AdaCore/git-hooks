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
        assert p.status == 0, p.image

        # Verify that subm is a directory that exists...
        self.assertTrue(isdir('subm'),
                        p.image + '\n' + Run(['ls -la'.split()]).cmd_out)

        # Now that the setup phase is done, commit the change.
        p = Run(['git', 'commit', '-m', 'Add submodule subm'])
        assert p.status == 0, p.image

        # Get the hash of our submodule commit.  We will need it
        # to match the output of the push command.
        p = Run(['git rev-parse HEAD'.split()])
        assert p.status == 0, p.image
        subm_rev = p.out.strip()

        # Also get the "author date" for our commit.  We need this
        # info as part of the expected output.
        p = Run(['git log -n1 --pretty=format:%ad'.split()])
        assert p.status == 0, p.image
        author_date = p.out.strip()

        # Same for the hash of the .gitmodules file...
        p = Run(['git ls-tree HEAD .gitmodules'.split()])
        assert p.status == 0, p.image
        gitmodules_hash = p.out.split()[2]

        # For coverage purposes, we want to test the calling of
        # the style-check program via the regular method (where
        # GIT_HOOKS_STYLE_CHECKER is not defined. Ideally, we would
        # still like to provide our own, and we try doing so by
        # updating PATH with the path to our own cvs_check script.
        # But this only works on machines where the cvs_check
        # script is NOT installed in the standard location, because
        # the "update" hook inserts the standard cvs_check path
        # at the start of the PATH.
        #
        # This means that, on machines with cvs_check installed,
        # deleting GIT_HOOKS_STYLE_CHECKER will cause the real cvs_check
        # to be called, whereas our fake cvs_check will be called
        # on all other machines. For matching purposes of the
        # expected output, both scripts must produce the same output.
        del os.environ['GIT_HOOKS_STYLE_CHECKER']
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
remote: DEBUG: style_check_commit(old_rev=7a373b536b65b600a449b5c739c137301f6fd364, new_rev=%(subm_rev)s)
remote:   DEBUG: subproject entry ignored: subm
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=7a373b536b65b600a449b5c739c137301f6fd364
remote:                         new_rev=%(subm_rev)s)
remote: DEBUG: update base: 7a373b536b65b600a449b5c739c137301f6fd364
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add submodule subm
remote: X-Act-Checkin: repo
remote: X-Git-Author: hooks tester <hooks-tester@example.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 7a373b536b65b600a449b5c739c137301f6fd364
remote: X-Git-Newrev: %(subm_rev)s
remote:
remote: commit %(subm_rev)s
remote: Author: hooks tester <hooks-tester@example.com>
remote: Date:   %(author_date)s
remote:
remote:     Add submodule subm
remote:
remote: Diff:
remote: ---
remote:  .gitmodules | 3 +++
remote:  subm        | 1 +
remote:  2 files changed, 4 insertions(+)
remote:
remote: diff --git a/.gitmodules b/.gitmodules
remote: new file mode 100644
remote: index 0000000..%(gitmodules_short_hash)s
remote: --- /dev/null
remote: +++ b/.gitmodules
remote: @@ -0,0 +1,3 @@
remote: +[submodule "subm"]
remote: +	path = subm
remote: +	url = %(TEST_DIR)s/bare/subm.git
remote: diff --git a/subm b/subm
remote: new file mode 160000
remote: index 0000000..8adf3db
remote: --- /dev/null
remote: +++ b/subm
remote: @@ -0,0 +1 @@
remote: +Subproject commit 8adf3dbfb04e35b0322bdcc12e96d1493f6e4502
To ../bare/repo.git
   7a373b5..%(short_subm_rev)s  master -> master
""" % {'subm_rev' : subm_rev,
       'short_subm_rev' : subm_rev[0:7],
       'author_date' : author_date,
       'gitmodules_short_hash' : gitmodules_hash[:7],
       'TEST_DIR' : TEST_DIR,
      }

        assert p.status == 0, p.image
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
