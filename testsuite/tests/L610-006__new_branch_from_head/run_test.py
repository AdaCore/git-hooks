        p = testcase.run(
            "git show-ref -s release-0.1-branch".split(), cwd=testcase.bare_repo_dir
        )