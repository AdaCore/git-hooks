import os


def test_push_new_branch(testcase):
    """Try pushing a new branch which creates no new commit at all."""
    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin my-topic".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'my-topic'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/my-topic
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:
remote: The branch 'my-topic' was created pointing to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 * [new branch]      my-topic -> my-topic
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Add testing of manual commit email resending (for UC02-038).
    #
    # For that, we simulate user going into the bare repository,
    # and calling the post-receive hook with the correct parameters
    # for resending the emails from the push above.

    resending_environ = {
        "GIT_HOOKS_EMAIL_REPLAY_REASON": "short reason",
    }

    sha1_before = "0000000000000000000000000000000000000000"
    sha1_after = "d065089ff184d97934c010ccd0e7e8ed94cb7165"
    ref_name = "refs/heads/my-topic"

    p = testcase.run(
        [os.path.join(testcase.bare_repo_dir, "hooks", "post-receive")],
        input=f"|{sha1_before} {sha1_after} {ref_name}",
        cwd=testcase.bare_repo_dir,
        env=resending_environ,
    )

    expected_out = """\
DEBUG: Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
From: Test Suite <testsuite@adacore.com>
To: git-hooks-ci@example.com
Subject: [repo] Created branch 'my-topic'
X-Act-Checkin: repo
X-Git-Author: Test Suite <testsuite@adacore.com>
X-Git-Refname: refs/heads/my-topic
X-Git-Oldrev: 0000000000000000000000000000000000000000
X-Git-Newrev: d065089ff184d97934c010ccd0e7e8ed94cb7165

======================================================================
==  WARNING: THIS EMAIL WAS MANUALLY RE-SENT (TICK-ET#)]
==
==  The email's date is therefore NOT representative of when
==  the corresponding update was actually pushed to the repository.
======================================================================

The branch 'my-topic' was created pointing to:

 d065089... New file: a.
"""
