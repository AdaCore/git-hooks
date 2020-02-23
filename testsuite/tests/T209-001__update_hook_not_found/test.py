from support import *

import os


class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try an update when update-hook points to a non-existant script.
        """
        cd ('%s/repo' % TEST_DIR)

        # First, adjust the project.config file to use an update-hook
        # script.  We have to do it manually here because we want to
        # provide a name of a script we are sure does not exist.
        bad_update_hook_filename = os.path.abspath('bad-update-hook')
        assert not os.path.exists(bad_update_hook_filename)

        with open('%s/hooks_config' % TEST_DIR) as f:
            project_config = f.read() % {
                'hook_filename': bad_update_hook_filename}
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
remote: *** Invalid hooks.update-hook configuration, no such file:
remote: *** {hook_filename}
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(hook_filename=bad_update_hook_filename)

        self.assertTrue(p.status != 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
