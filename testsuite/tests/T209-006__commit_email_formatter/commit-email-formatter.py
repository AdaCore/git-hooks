#! /usr/bin/env python
import sys
import json

cli_args = sys.argv[1:]
stdin_data = sys.stdin.read()

commit_data = json.loads(stdin_data)


def commit_data_image():
    """A small function returning a string representation of commit_data.

    The data is formatted in such as way that it's somewhat easy to read.
    """
    result = []
    for key, value in sorted(commit_data.items()):

        if key in ("body", "email_default_body", "email_default_diff"):
            if value is not None and len(value.splitlines()) > 1:
                value = "<multiline>\n" + "".join(
                    "   | {line}".format(line=line) for line in value.splitlines(True)
                )
        result.append("* {key}: {value}".format(key=key, value=value))
    return "\n".join(result)


# By default, this script changes nothing in the commit email.
# Then, depending on the commit, it exercises various scenarios
# of pieces of the email being customized.
result = {}

if 'Add "Introduction" section title' in commit_data["subject"]:
    # Replace everything. We intentionally do not set "diff"
    # to verify that the default is as expected.
    result["email_subject"] = "New subject: Add intro"
    result["email_body"] = "My customized email body\n(with diff)\n"

elif "Improve introduction" in commit_data["subject"]:
    # Just replace the subject, keeping the rest of the body exactly
    # the same. Force "diff" to be the same as "email_default_diff".
    result["email_subject"] = "New subject:" + commit_data["subject"]
    result["diff"] = commit_data["email_default_diff"]

elif "Add new file: b" in commit_data["subject"]:
    # Replace the body, and disable the diff.
    result["email_body"] = "New Body\n\n[Diff removed for reason X and Y]"
    result["diff"] = None

elif "(no-diff-in-email)" in commit_data["body"]:
    result["diff"] = None

elif "(dump_hook_data)" in commit_data["subject"]:
    result["email_body"] = commit_data_image()
    result["diff"] = "[Diff suppressed for reason X or Y]"

elif commit_data["ref_kind"] == "notes":
    result["email_subject"] = "Customized notes email subject"
    result["email_body"] = commit_data_image()
    result["diff"] = None

elif "(email-formatter:return-nonzero)" in commit_data["subject"]:
    print("Something went wrong, ouh la la, this is me crashing, no good!")
    sys.exit(1)

elif "(email-formatter:return-bad-json)" in commit_data["subject"]:
    print("{")
    sys.exit(0)

elif "(email-formatter:return-not-dict)" in commit_data["subject"]:
    print("[1, 2, 3]")
    sys.exit(0)

print(json.dumps(result))
