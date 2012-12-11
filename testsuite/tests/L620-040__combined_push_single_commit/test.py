from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        self.set_debug_level(1)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, d065089ff184d97934c010ccd0e7e8ed94cb7165, a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: DEBUG: (combined style checking)
remote: DEBUG: check_commit(old_rev=d065089ff184d97934c010ccd0e7e8ed94cb7165, new_rev=a60540361d47901d3fe254271779f380d94645f7)
remote: *** cvs_check: `trunk/repo/a'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:                         new_rev=a60540361d47901d3fe254271779f380d94645f7)
remote: DEBUG: update base: d065089ff184d97934c010ccd0e7e8ed94cb7165
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
