def test_push_meta_config_and_master(testcase):
    """Try pushing refs/meta/config at same time as other branch"""
    # Do a simple "git push" without any information about the remote
    # or the references to push; in that case, the (non-bare) repository
    # has been configured via its .git/config file so that two references
    # get pushed, with one of the references to update being the special
    # reference refs/meta/config. We expect this update attempt to be
    # rejected.
    p = testcase.run("git push".split())
    expected_out = """\
remote: *** You are trying to push multiple references at the same time:
remote: ***   - refs/heads/master
remote: ***   - refs/meta/config
remote: ***
remote: *** Updates to the refs/meta/config reference must be pushed
remote: *** on their own. Please push this reference first, and then
remote: *** retry pushing the remaining references.
To ../bare/repo.git
 ! [remote rejected] master -> master (pre-receive hook declined)
 ! [remote rejected] meta/config -> refs/meta/config (pre-receive hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Now, push the refs/meta/config update on its own, as requested.

    p = testcase.run("git push origin meta/config:refs/meta/config".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Add small comment.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 87e99cb2e262923270df3695ec90d7cd45d41e22
remote: X-Git-Newrev: dbef16c19366556f9e0bfa7ff57ce9484dd1262e
remote:
remote: commit dbef16c19366556f9e0bfa7ff57ce9484dd1262e
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Mon Dec 30 08:04:51 2013 +0400
remote:
remote:     Add small comment.
remote:
remote: Diff:
remote: ---
remote:  project.config | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/project.config b/project.config
remote: index e565530..73f544e 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -1,4 +1,5 @@
remote:  [hooks]
remote: +        # Standard minimum configuration.
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
remote:          filer-email = filer@example.com
To ../bare/repo.git
   87e99cb..dbef16c  meta/config -> refs/meta/config
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # And now that the refs/meta/config update is out of the way,
    # the simple "git push" command we tried earlier should work,
    # now.

    p = testcase.run("git push".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..a605403  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
