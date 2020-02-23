from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # First, adjust the project.config file to use an update-hook
        # script.  We have to do it manually here, because we need to
        # provide the full path to that script.
        with open('%s/hooks_config' % TEST_DIR) as f:
            project_config = f.read() % {'TEST_DIR': TEST_DIR}
        with open('project.config', 'w') as f:
            f.write(project_config)
        p = Run(['git', 'commit', '-m', 'Add hooks.update-hook config',
                 'project.config'])
        self.assertTrue(p.status == 0, p.image)

        p = Run(['git', 'push', 'origin',
                 'refs/heads/meta/config:refs/meta/config'])
        self.assertTrue(p.status == 0, p.image)

        p = Run('git checkout master'.split())
        self.assertTrue(p.status == 0, p.image)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** Update rejected by this repository's hooks.update-hook script
remote: *** ({TEST_DIR}/update-hook):
remote: *** -----[ update-hook args ]-----
remote: *** 'refs/heads/master'
remote: *** '426fba3571947f6de7f967e885a3168b9df7004a'
remote: *** 'dd6165c96db712d3e918fb5c61088b171b5e7cab'
remote: *** -----[ update-hook stdin ]-----
remote: *** -----[ update-hook end ]-----
remote: *** Error: Updates of this branch (refs/heads/master) are not allowed.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(TEST_DIR=TEST_DIR)

        self.assertTrue(p.status != 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
