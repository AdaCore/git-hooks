from support import *

class TestRun(TestCase):
    def test_push_refs_meta_config_update(self):
        """Try pushing an update of the refs/meta/config:project.config file
        """
        cd ('%s/repo' % TEST_DIR)

        # Push an update to the refs/meta/config reference, where
        # we modify the hooks's configuration file. The goal of
        # this test is to verify that the new configuration is
        # immediately taken into account (i.e. applied to this update
        # as well) -- in particular, the config.mailinglist gets
        # changed from git-hooks-ci@example.com to super-ci@example.com.
        # Verify that the email gets sent to that address, rather than
        # the older one.
        p = Run('git push origin meta/config:refs/meta/config'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: super-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Change hooks.mailinglist config
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 6998dc7254553c752c65e3f5ded4fbc364f7af13
remote: X-Git-Newrev: f8be2d0a7b34c24146f28782a3fd0515c34a93ee
remote:
remote: commit f8be2d0a7b34c24146f28782a3fd0515c34a93ee
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 30 08:04:51 2013 +0400
remote:
remote:     Change hooks.mailinglist config
remote:
remote: Diff:
remote: ---
remote:  project.config | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/project.config b/project.config
remote: index 05e3cbe..f06455a 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,4 +1,4 @@
remote:  [hooks]
remote:          from-domain = adacore.com
remote: -        mailinglist = git-hooks-ci@example.com
remote: +        mailinglist = super-ci@example.com
remote:  	filer-email = filer@example.com
To ../bare/repo.git
   6998dc7..f8be2d0  meta/config -> refs/meta/config
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
