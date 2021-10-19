def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: *** cvs_check: `repo' < `c' `d'
remote: *** cvs_check: `repo' < `c'
remote: *** cvs_check: `repo' < `d'
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/mas.*',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/master).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
