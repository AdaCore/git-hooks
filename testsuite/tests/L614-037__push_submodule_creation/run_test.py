        p = testcase.run(
            ["git", "submodule", "add", "%s/bare/subm.git" % testcase.work_dir]
        )
        assert isdir(os.path.join(testcase.repo_dir, "subm")), (
            p.image
            + "\n"
            + testcase.run(["ls -la".split()], cwd=testcase.repo_dir).cmd_out
        )
        os.environ["PATH"] = testcase.work_dir + ":" + os.environ["PATH"]
remote: +	url = %(testcase.work_dir)s/bare/subm.git
            "testcase.work_dir": testcase.work_dir,