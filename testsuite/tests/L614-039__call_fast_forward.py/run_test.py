import sys


def test_call_fast_foward_py(testcase):
    """Test calling fast_forward.py many ways."""
    # First, call it with the wrong usage...
    p = testcase.run(
        [sys.executable, "hooks/fast_forward.py"], cwd=testcase.bare_repo_dir
    )
    testcase.assertNotEqual(p.status, 0, p.image)

    # Next, call it with an OK fast-forward...
    p = testcase.run(
        [
            sys.executable,
            "hooks/fast_forward.py",
            "refs/heads/master",
            "d065089ff184d97934c010ccd0e7e8ed94cb7165",
            "a60540361d47901d3fe254271779f380d94645f7",
        ],
        cwd=testcase.bare_repo_dir,
    )
    expected_out = """\

"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Call fast_forward.py with an invalid fast-forward
    # (just reversing the arguments above)...
    p = testcase.run(
        [
            sys.executable,
            "hooks/fast_forward.py",
            "refs/heads/master",
            "a60540361d47901d3fe254271779f380d94645f7",
            "d065089ff184d97934c010ccd0e7e8ed94cb7165",
        ],
        cwd=testcase.bare_repo_dir,
    )
    expected_out = """\
*** Non-fast-forward updates are not allowed for this reference.
*** Please rebase your changes on top of the latest HEAD,
*** and then try pushing again.
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
