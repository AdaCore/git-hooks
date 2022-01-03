def test_push_commits_on_master(testcase):
    # Push the commit adding the style-checker-config-file option
    # to the refs/meta/config branch. However, the file it points
    # to does not exist in that reference, nor is is added by
    # the commit we're pusing. So this should be rejected.

    p = testcase.run("git push origin meta-config-missing:refs/meta/config".split())
    expected_out = """\
remote: *** Cannot find style_checker config file: `style.yaml'.
remote: ***
remote: *** Your repository is configured to provide a configuration file to
remote: *** the style_checker; however, this configuration file (style.yaml)
remote: *** cannot be found in commit 3ff58556a322e274f56e7224b9ac74fae5011cc3.
remote: ***
remote: *** Perhaps you haven't added this configuration file to this branch
remote: *** yet?
remote: error: hook declined to update refs/meta/config
To ../bare/repo.git
 ! [remote rejected] meta-config-missing -> refs/meta/config (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Do the same as above, but this time with a commit which
    # provides both the config file at the same time it adds
    # the style-checker-config-file option.  This time, the update
    # should be accepted.

    p = testcase.run("git push origin meta-config:refs/meta/config".split())
    expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `project.config' `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Add style-checker-config-file option
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: ac4cd5a2fc6c5da2e40978e188a8b015eaee6406
remote: X-Git-Newrev: 9142bec495ff0a6d26ecd91a43214d3274ec98a6
remote:
remote: commit 9142bec495ff0a6d26ecd91a43214d3274ec98a6
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 9 07:29:59 2017 +0100
remote:
remote:     Add style-checker-config-file option
remote:
remote: Diff:
remote: ---
remote:  project.config | 1 +
remote:  style.yaml     | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/project.config b/project.config
remote: index e565530..53aad56 100644
remote: --- a/project.config
remote: +++ b/project.config
remote: @@ -2,3 +2,4 @@
remote:          from-domain = adacore.com
remote:          mailinglist = git-hooks-ci@example.com
remote:          filer-email = filer@example.com
remote: +        style-checker-config-file = style.yaml
remote: diff --git a/style.yaml b/style.yaml
remote: new file mode 100644
remote: index 0000000..b3fcae2
remote: --- /dev/null
remote: +++ b/style.yaml
remote: @@ -0,0 +1 @@
remote: +# A YaML file (with nothing in it)
To ../bare/repo.git
   ac4cd5a..9142bec  meta-config -> refs/meta/config
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Push a commit to the repository to a branch where
    # the style checker's config file does not exist yet...

    p = testcase.run("git push origin step-1/checker_config_missing:master".split())
    expected_out = """\
remote: *** Cannot find style_checker config file: `style.yaml'.
remote: ***
remote: *** Your repository is configured to provide a configuration file to
remote: *** the style_checker; however, this configuration file (style.yaml)
remote: *** cannot be found in commit 555923ece17519f0afeed78625afc6ab7e64e592.
remote: ***
remote: *** Perhaps you haven't added this configuration file to this branch
remote: *** yet?
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] step-1/checker_config_missing -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Once the checkin above did not work, push a commit which
    # adds the missing config file (on its own)

    p = testcase.run("git push origin step-2/add_checker_config_file:master".split())
    expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add style.yaml (auxillary config file for the style_checker)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: b3a13b32c1b76333cdf5135381a20b98c41f9897
remote: X-Git-Newrev: c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote:
remote: commit c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:09:34 2017 +0400
remote:
remote:     Add style.yaml (auxillary config file for the style_checker)
remote:
remote: Diff:
remote: ---
remote:  style.yaml | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/style.yaml b/style.yaml
remote: new file mode 100644
remote: index 0000000..b3fcae2
remote: --- /dev/null
remote: +++ b/style.yaml
remote: @@ -0,0 +1 @@
remote: +# A YaML file (with nothing in it)
To ../bare/repo.git
   b3a13b3..c84b233  step-2/add_checker_config_file -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Once the config file is in, we should now be able to push
    # our commit, this time.

    p = testcase.run("git push origin step-3/try_initial_commit_again:master".split())
    expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `b.adb'
remote: *** # A YaML file (with nothing in it)
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] b.adb: Print message when done.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: c84b233ceaf4009eb923d25fbbb632ddc1daa4aa
remote: X-Git-Newrev: bf95cd2158bada71f60ae9f742370452b46c4582
remote:
remote: commit bf95cd2158bada71f60ae9f742370452b46c4582
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Dec 9 07:23:40 2017 +0100
remote:
remote:     b.adb: Print message when done.
remote:
remote: Diff:
remote: ---
remote:  b.adb | 2 ++
remote:  1 file changed, 2 insertions(+)
remote:
remote: diff --git a/b.adb b/b.adb
remote: index 20a8315..df29668 100644
remote: --- a/b.adb
remote: +++ b/b.adb
remote: @@ -1,5 +1,7 @@
remote:  with A;
remote: +with GNAT.IO; use GNAT.IO;
remote:  procedure B is
remote:  begin
remote:     A.Gloval_Bar := @ + 1;
remote: +   Put_Line ("Done!");
remote:  end B;
To ../bare/repo.git
   c84b233..bf95cd2  step-3/try_initial_commit_again -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Simulate a change where we only change the config file...
    # We expect that config file to be effective immediately,
    # so we verify that the contents of that file as passed
    # to our style_checker (cvs_check in our testsuite) shows
    # the updated contents.

    p = testcase.run("git push origin step-4/modify_checker_config_only:master".split())
    expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: *** hello: world
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] style.yaml: Set "hello" to "world".
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: bf95cd2158bada71f60ae9f742370452b46c4582
remote: X-Git-Newrev: 2e2c5c515364d94be300928ffc9507834843acdf
remote:
remote: commit 2e2c5c515364d94be300928ffc9507834843acdf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:17:00 2017 +0400
remote:
remote:     style.yaml: Set "hello" to "world".
remote:
remote: Diff:
remote: ---
remote:  style.yaml | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/style.yaml b/style.yaml
remote: index b3fcae2..817407e 100644
remote: --- a/style.yaml
remote: +++ b/style.yaml
remote: @@ -1 +1,2 @@
remote:  # A YaML file (with nothing in it)
remote: +hello: world
To ../bare/repo.git
   bf95cd2..2e2c5c5  step-4/modify_checker_config_only -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # And finally, simulate a commit which changes both the config
    # file and other files.
    #
    # Same as above, we expect the update config file to be effective
    # immediately, so we verify that the contents of that file as
    # passed to our style_checker (cvs_check in our testsuite) shows
    # the updated contents.

    p = testcase.run(
        "git push origin step-5/modify_code_and_checker_config:master".split()
    )
    expected_out = """\
remote: *** cvs_check: `--config' `style.yaml' `repo' < `a.ads' `style.yaml'
remote: *** # A YaML file (with nothing in it)
remote: *** hello: world
remote: *** something: else
remote: ***
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] set Global_Var's initial value to 20 and adapt style.yaml
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 2e2c5c515364d94be300928ffc9507834843acdf
remote: X-Git-Newrev: bdd1bbb4ec3cc746bf2c26d8d204ec6cd6d86553
remote:
remote: commit bdd1bbb4ec3cc746bf2c26d8d204ec6cd6d86553
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 13 16:17:54 2017 +0400
remote:
remote:     set Global_Var's initial value to 20 and adapt style.yaml
remote:
remote: Diff:
remote: ---
remote:  a.ads      | 2 +-
remote:  style.yaml | 1 +
remote:  2 files changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a.ads b/a.ads
remote: index 2153543..c63a723 100644
remote: --- a/a.ads
remote: +++ b/a.ads
remote: @@ -1,3 +1,3 @@
remote:  package A is
remote: -   Gloval_Bar : Integer := 15;
remote: +   Gloval_Bar : Integer := 20;
remote:  end A;
remote: diff --git a/style.yaml b/style.yaml
remote: index 817407e..1097710 100644
remote: --- a/style.yaml
remote: +++ b/style.yaml
remote: @@ -1,2 +1,3 @@
remote:  # A YaML file (with nothing in it)
remote:  hello: world
remote: +something: else
To ../bare/repo.git
   2e2c5c5..bdd1bbb  step-5/modify_code_and_checker_config -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
