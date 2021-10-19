def test_push_refs_meta_config_update(testcase):
    """Try pushing an update of the refs/meta/config:project.config file"""
    # Push an update to the refs/meta/config reference, where
    # we modify the hooks's configuration file. The goal of
    # this test is to verify that the new configuration is
    # immediately taken into account (i.e. applied to this update
    # as well) -- in particular, the config.mailinglist gets
    # changed from git-hooks-ci@example.com to super-ci@example.com.
    # Verify that the email gets sent to that address, rather than
    # the older one.
    p = testcase.run("git push origin meta/config:refs/meta/config".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: super-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Change hooks.mailinglist config
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: adff0b9f9efecebd5a0d2e049e4251582bbb6bb9
remote: X-Git-Newrev: e11c90acd878192c880d71a3426d094be4d64bf7
remote:
remote: commit e11c90acd878192c880d71a3426d094be4d64bf7
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
remote: index e565530..c85ce41 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,4 +1,4 @@
remote:  [hooks]
remote:          from-domain = adacore.com
remote: -        mailinglist = git-hooks-ci@example.com
remote: +        mailinglist = super-ci@example.com
remote:          filer-email = filer@example.com
To ../bare/repo.git
   adff0b9..e11c90a  meta/config -> refs/meta/config
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
