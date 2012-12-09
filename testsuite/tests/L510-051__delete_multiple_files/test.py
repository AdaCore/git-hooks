from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that certain files are not being checked
        # because they are being deleted.
        self.set_debug_level(2)

        p = Run('git push origin master'.split())
        expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: DEBUG: validate_ref_update (refs/heads/master, f82624871b6cfc46d5a7c5be518bc20e8f42be42, 0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote:   DEBUG: deleted file ignored: a.adb
remote:   DEBUG: deleted file ignored: b.adb
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote:                         new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   f826248..0c702ad  master -> master
"""
        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
