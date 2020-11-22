import os
from support import cd, Run, runtests, TestCase, TEST_DIR


class TestRun(TestCase):
    def test_commit_commit_email_formatter(self):
        """Test the hooks.commit-email-formatter hook.

        The purpose of this testcase is to perform a sanity check
        of the behavior of the git-hooks when a user pushes some changes
        to a repository where the hooks.commit-email-formatter config
        option is set.

        The script we use for that is called commit-email-formatter.py,
        and was written to facilitate testing of the various possible
        scenarios we want to support with this commit-email-formatter
        hook. It does so by inspecting the various commits and react
        differently based on the commit (generally speaking, it takes
        cues from the commit's revision log).
        """
        cd('%s/repo' % TEST_DIR)

        # First, update the git-hooks configuration to install our
        # the script we want to use as our commit-email-formatter.

        p = Run(['git', 'fetch', 'origin', 'refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'checkout', 'FETCH_HEAD'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'config', '--file', 'project.config',
                 'hooks.commit-email-formatter',
                 os.path.join(TEST_DIR, 'commit-email-formatter.py')])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'commit', '-m', 'Add hooks.commit-email-formatter',
                 'project.config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        self.assertTrue('HEAD -> refs/meta/config' in p.out.splitlines()[-1],
                        p.image)

        # Return our current HEAD to branch "master". Not critical for
        # our testing, but it helps the testcase be closer to the more
        # typical scenarios.
        p = Run(['git', 'checkout', 'master'])
        self.assertEqual(p.status, 0, p.image)

        # Push the "master" branch, which introduces a series of commits.
        # Each commit will be handled by our commit-email-formatter.py
        # script based on its contents, with the commits being created
        # so as to help us cover the whole range of options we support.
        # This makes for a fairly long list of commits, which means
        # a correspondingly long output. We are testing it this way
        # (one push of multiple commits) so as to verify that unexpected
        # behavior of the commit-email-formatter hook doesn't affect
        # the next commit.

        p = Run('git push origin master'.split())

        # Let's split the expected_out by commits, so we can add comments
        # describing each commit prior to being processed by our hook.
        expected_out = ""

        # | commit 433a74237b4d8849da6bd33f6cfdda1919086358
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 10:27:19 2020 -0700
        # |
        # |     Add "Introduction" section title
        #
        # We expected the subject and email body to be customized.
        # We should also see a "diff" section, even though the hook
        # didn't provide a value for "diff". This verifies that
        # we handle the default properly.

        expected_out += """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: New subject: Add intro
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: bb7753f79d9fbab15012afb1d8214ed0fec0a00d
remote: X-Git-Newrev: 433a74237b4d8849da6bd33f6cfdda1919086358
remote:
remote: My customized email body
remote: (with diff)
remote:
remote: Diff:
remote: ---
remote:  a | 3 +++
remote:  1 file changed, 3 insertions(+)
remote:
remote: diff --git a/a b/a
remote: index 18832d3..286976e 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1 +1,4 @@
remote: +Introduction
remote: +============
remote: +
remote:  Hello.
"""

        # | commit 5fee44f6ec23bde253ac8e4a80fb10c5b7469e48
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 10:34:59 2020 -0700
        # |
        # |     Improve introduction
        #
        # We expect the subject to be customized, and the rest should be
        # the same as the default commit email.

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: New subject:Improve introduction
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 433a74237b4d8849da6bd33f6cfdda1919086358
remote: X-Git-Newrev: 5fee44f6ec23bde253ac8e4a80fb10c5b7469e48
remote:
remote: commit 5fee44f6ec23bde253ac8e4a80fb10c5b7469e48
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 10:34:59 2020 -0700
remote:
remote:     Improve introduction
remote:
remote: Diff:
remote: ---
remote:  a | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 286976e..a7cd38e 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,4 +1,4 @@
remote:  Introduction
remote:  ============
remote:
remote: -Hello.
remote: +Hello. This is going to be a useful document.
"""

        # | commit 3a81561f42669f8ae85304a67ca30225afe780f9
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 10:36:43 2020 -0700
        # |
        # |     Add new file: b
        #
        # The email body should be customized, and the "Diff: section should
        # be absent (because the hook returned "diff" set to None).

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add new file: b
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 5fee44f6ec23bde253ac8e4a80fb10c5b7469e48
remote: X-Git-Newrev: 3a81561f42669f8ae85304a67ca30225afe780f9
remote:
remote: New Body
remote:
remote: [Diff removed for reason X and Y]
"""

        # | commit 83b7d3bc13428241abb3f27aad2e226c809e5e56
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:31:49 2020 -0700
        # |
        # |     Update b
        # |
        # |     (no-diff-in-email)
        #
        # We expect the email to be the same as the default email,
        # except that the "diff" section has been removed.
        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Update b
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 3a81561f42669f8ae85304a67ca30225afe780f9
remote: X-Git-Newrev: 83b7d3bc13428241abb3f27aad2e226c809e5e56
remote:
remote: commit 83b7d3bc13428241abb3f27aad2e226c809e5e56
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:31:49 2020 -0700
remote:
remote:     Update b
remote:
remote:     (no-diff-in-email)
remote:
"""

        # | commit 6b65d08866b52c750df5ace3f18357133e352b4e
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:34:01 2020 -0700
        # |
        # |     Update a
        #
        # A commit with nothing in particular. The hook should return
        # an empty dict, signifying that nothing should be customized
        # (meaning, the standard email should get sent).
        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Update a
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 83b7d3bc13428241abb3f27aad2e226c809e5e56
remote: X-Git-Newrev: 6b65d08866b52c750df5ace3f18357133e352b4e
remote:
remote: commit 6b65d08866b52c750df5ace3f18357133e352b4e
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:34:01 2020 -0700
remote:
remote:     Update a
remote:
remote: Diff:
remote: ---
remote:  a | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index a7cd38e..579abc9 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,4 +1,4 @@
remote:  Introduction
remote:  ============
remote:
remote: -Hello. This is going to be a useful document.
remote: +Hello. This is going to be a useful document for everyone to read.
"""

        # | commit 4131b4399e258bd3c36119d026455a4abce2e971
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:37:44 2020 -0700
        # |
        # |     Improve b (email-formatter:return-nonzero)
        #
        # This commit will cause the hook to return nonzero.
        #
        # In that situation, the git-hooks are expected to fall back
        # to the default commit email, with a warning at the end of
        # the email body (but before the diff).

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Improve b (email-formatter:return-nonzero)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 6b65d08866b52c750df5ace3f18357133e352b4e
remote: X-Git-Newrev: 4131b4399e258bd3c36119d026455a4abce2e971
remote:
remote: commit 4131b4399e258bd3c36119d026455a4abce2e971
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:37:44 2020 -0700
remote:
remote:     Improve b (email-formatter:return-nonzero)
remote:
remote: | WARNING:
remote: | hooks.commit-email-formatter returned nonzero: 1.
remote: | Falling back to default email format.
remote: |
remote: | $ {TEST_DIR}/commit-email-formatter.py refs/heads/master 4131b4399e258bd3c36119d026455a4abce2e971
remote: | Something went wrong, ouh la la, this is me crashing, no good!
remote: |
remote:
remote: Diff:
remote: ---
remote:  b | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/b b/b
remote: index 3639688..cc5e45c 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1 +1,2 @@
remote:  New file with some interesting contents.
remote: +Let's start with some background: dark.
""".format(TEST_DIR=TEST_DIR)

        # | commit 3d75bd9d3a551d8b66b8ec7b79eedc7496bb804f
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:40:46 2020 -0700
        # |
        # |     Improve introduction once more
        #
        # A commit for which no error is expected, to verify that
        # the error handling in the previous commit does not affect
        # the handling of this commit.
        #
        # The subject is set up so as to "trigger" commit-email-formatter.py
        # to customize the subject and force the diff (which was the default
        # anyway).

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: New subject:Improve introduction once more
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4131b4399e258bd3c36119d026455a4abce2e971
remote: X-Git-Newrev: 3d75bd9d3a551d8b66b8ec7b79eedc7496bb804f
remote:
remote: commit 3d75bd9d3a551d8b66b8ec7b79eedc7496bb804f
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:40:46 2020 -0700
remote:
remote:     Improve introduction once more
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index 579abc9..3ef8ed1 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -2,3 +2,4 @@ Introduction
remote:  ============
remote:
remote:  Hello. This is going to be a useful document for everyone to read.
remote: +It will provide detailed information on this thing.
"""

        # | commit ee3e1d03e6decce59fce06f3a2fe256f0221cb80
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:42:05 2020 -0700
        # |
        # |     continue improving B (email-formatter:return-bad-json)
        #
        # This commit will cause the hook to return some output which
        # is not valid JSON.
        #
        # In that situation, the git-hooks are expected to fall back
        # to the default commit email, with a warning at the end of
        # the email body (but before the diff).
        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] continue improving B (email-formatter:return-bad-json)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 3d75bd9d3a551d8b66b8ec7b79eedc7496bb804f
remote: X-Git-Newrev: ee3e1d03e6decce59fce06f3a2fe256f0221cb80
remote:
remote: commit ee3e1d03e6decce59fce06f3a2fe256f0221cb80
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:42:05 2020 -0700
remote:
remote:     continue improving B (email-formatter:return-bad-json)
remote:
remote: | WARNING:
remote: | hooks.commit-email-formatter returned invalid JSON.
remote: | Falling back to default email format.
remote: |
remote: | $ {TEST_DIR}/commit-email-formatter.py refs/heads/master ee3e1d03e6decce59fce06f3a2fe256f0221cb80
remote: | {{
remote: |
remote:
remote: Diff:
remote: ---
remote:  b | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/b b/b
remote: index cc5e45c..f20781f 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,2 +1,3 @@
remote:  New file with some interesting contents.
remote:  Let's start with some background: dark.
remote: +Let's then look at the foreground: Bright colorful.
""".format(TEST_DIR=TEST_DIR)

        # | commit e617216033a96c18bad5b2235d960c784dd3efa7
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:46:51 2020 -0700
        # |
        # |     more information in b.
        # |
        # |     (no-diff-in-email)
        #
        # A commit for which no error is expected, to verify that
        # the error handling in the previous commit does not affect
        # the handling of this commit.
        #
        # The email should be as per the default, except that the "Diff:"
        # section is omitted.

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] more information in b.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: ee3e1d03e6decce59fce06f3a2fe256f0221cb80
remote: X-Git-Newrev: e617216033a96c18bad5b2235d960c784dd3efa7
remote:
remote: commit e617216033a96c18bad5b2235d960c784dd3efa7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:46:51 2020 -0700
remote:
remote:     more information in b.
remote:
remote:     (no-diff-in-email)
remote:
"""

        # | commit c47a7f0a65557eb1551b5fd80e753d81c529c69a
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:49:14 2020 -0700
        # |
        # |     More [snip snip] (email-formatter:return-not-dict)
        #
        # This commit will cause the hook to return nonzero.
        #
        # In that situation, the git-hooks are expected to fall back
        # to the default commit email, with a warning at the end of
        # the email body (but before the diff).

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] More text in a's introduction section
remote:  (email-formatter:return-not-dict)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: e617216033a96c18bad5b2235d960c784dd3efa7
remote: X-Git-Newrev: c47a7f0a65557eb1551b5fd80e753d81c529c69a
remote:
remote: commit c47a7f0a65557eb1551b5fd80e753d81c529c69a
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:49:14 2020 -0700
remote:
remote:     More text in a's introduction section (email-formatter:return-not-dict)
remote:
remote: | WARNING:
remote: | hooks.commit-email-formatter output is not JSON dict.
remote: | Falling back to default email format.
remote: |
remote: | $ {TEST_DIR}/commit-email-formatter.py refs/heads/master c47a7f0a65557eb1551b5fd80e753d81c529c69a
remote: | [1, 2, 3]
remote: |
remote:
remote: Diff:
remote: ---
remote:  a | 3 ++-
remote:  1 file changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 3ef8ed1..5a94736 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -2,4 +2,5 @@ Introduction
remote:  ============
remote:
remote:  Hello. This is going to be a useful document for everyone to read.
remote: -It will provide detailed information on this thing.
remote: +It will provide detailed information on this thing, including
remote: +information that you might never have thought about.
""".format(TEST_DIR=TEST_DIR)

        # | commit 699356fb0903efbe73a18e2573a9ca67bc7c35a5 (HEAD -> master)
        # | Author: Joel Brobecker <brobecker@adacore.com>
        # | Date:   Sun Aug 2 14:52:44 2020 -0700
        # |
        # |     Provide information about the sky (no-diff-in-email)
        #
        # A commit for which no error is expected, to verify that
        # the error handling in the previous commit does not affect
        # the handling of this commit.
        #
        # The email should be as per the default, except that the "diff"
        # section is omitted.

        expected_out += """\
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Provide information about the sky (no-diff-in-email)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: c47a7f0a65557eb1551b5fd80e753d81c529c69a
remote: X-Git-Newrev: 699356fb0903efbe73a18e2573a9ca67bc7c35a5
remote:
remote: commit 699356fb0903efbe73a18e2573a9ca67bc7c35a5
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Aug 2 14:52:44 2020 -0700
remote:
remote:     Provide information about the sky (no-diff-in-email)
remote:
To ../bare/repo.git
   bb7753f..699356f  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Now, push branch "hook-dump", which has a single commit
        # whose subject is such that commit-email-formatter.py will
        # know to replace the email's body with the data it was given
        # via stdin. While at it, it also exercises the replacement
        # of the "Diff:" section.

        p = Run('git push origin hook-dump'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'hook-dump'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/hook-dump
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: c7642aaf521a65fcd2414d1b9e51f7d51b881370
remote:
remote: The branch 'hook-dump' was created pointing to:
remote:
remote:  c7642aa... Update a (dump_hook_data).
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/hook-dump] Update a (dump_hook_data).
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/hook-dump
remote: X-Git-Oldrev: bb7753f79d9fbab15012afb1d8214ed0fec0a00d
remote: X-Git-Newrev: c7642aaf521a65fcd2414d1b9e51f7d51b881370
remote:
remote: * author_email: brobecker@adacore.com
remote: * author_name: Joel Brobecker
remote: * body: Update a (dump_hook_data).
remote: * email_default_body: <multiline>
remote:    | commit c7642aaf521a65fcd2414d1b9e51f7d51b881370
remote:    | Author: Joel Brobecker <brobecker@adacore.com>
remote:    | Date:   Sun Aug 2 18:26:31 2020 -0700
remote:    |
remote:    |     Update a (dump_hook_data).
remote:
remote: * email_default_diff: <multiline>
remote:    | ---
remote:    |  a | 2 +-
remote:    |  1 file changed, 1 insertion(+), 1 deletion(-)
remote:    |
remote:    | diff --git a/a b/a
remote:    | index 18832d3..c12abce 100644
remote:    | --- a/a
remote:    | +++ b/a
remote:    | @@ -1 +1 @@
remote:    | -Hello.
remote:    | +Hello there.
remote: * email_default_subject: [repo/hook-dump] Update a (dump_hook_data).
remote: * object_type: commit
remote: * ref_kind: branch
remote: * ref_name: refs/heads/hook-dump
remote: * rev: c7642aaf521a65fcd2414d1b9e51f7d51b881370
remote: * subject: Update a (dump_hook_data).
remote: Diff:
remote: [Diff suppressed for reason X or Y]
To ../bare/repo.git
 * [new branch]      hook-dump -> hook-dump
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a notes commit.
        #
        # Our commit-email-formatter.py script is expected to notice that
        # this is a notes commit, and customize the email's subject and
        # body (dumping the data given to the script), as well as suppress
        # the diff.

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: Customized notes email subject
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev:
remote: X-Git-Newrev: 91dd8e566584e81b1d6cd69fed5aa0b34e8ede3a
remote:
remote: * author_email: brobecker@adacore.com
remote: * author_name: Joel Brobecker
remote: * body: Notes added by 'git notes add'
remote: * email_default_body: <multiline>
remote:    | A Git note has been updated; it now contains:
remote:    |
remote:    |     Provide information missing from this commit's revision log (notes-commit)
remote:    |
remote:    | This note annotates the following commit:
remote:    |
remote:    | commit 699356fb0903efbe73a18e2573a9ca67bc7c35a5
remote:    | Author: Joel Brobecker <brobecker@adacore.com>
remote:    | Date:   Sun Aug 2 14:52:44 2020 -0700
remote:    |
remote:    |     Provide information about the sky (no-diff-in-email)
remote:
remote: * email_default_diff: <multiline>
remote:    |
remote:    | diff --git a/699356fb0903efbe73a18e2573a9ca67bc7c35a5 b/699356fb0903efbe73a18e2573a9ca67bc7c35a5
remote:    | new file mode 100644
remote:    | index 0000000..6314b20
remote:    | --- /dev/null
remote:    | +++ b/699356fb0903efbe73a18e2573a9ca67bc7c35a5
remote:    | @@ -0,0 +1 @@
remote:    | +Provide information missing from this commit's revision log (notes-commit)
remote: * email_default_subject: [notes][repo] Provide information about the sky (no-diff-in-email)
remote: * object_type: commit
remote: * ref_kind: notes
remote: * ref_name: refs/notes/commits
remote: * rev: 91dd8e566584e81b1d6cd69fed5aa0b34e8ede3a
remote: * subject: Notes added by 'git notes add'
To ../bare/repo.git
 * [new branch]      refs/notes/commits -> refs/notes/commits
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
