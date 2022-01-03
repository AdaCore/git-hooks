# -*- coding: utf-8 -*-


def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master."""
    p = testcase.run("git push origin master".split())
    expected_out = r"""remote: *** cvs_check: `repo' < `Mânü Scrîpt.txt'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: =?utf-8?b?W3JlcG9dIE3Dom7DvCBTY3LDrnB0LnR4dDogTmV3IGZpbGU=?=
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: df3425a769b5509cdac1d9bd0225cfe893f7b688
remote: X-Git-Newrev: 58067db29f84049f50761f13642a8e4116597276
remote:
remote: commit 58067db29f84049f50761f13642a8e4116597276
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 24 16:35:52 2020 +0400
remote:
remote:     Mânü Scrîpt.txt: New file
remote:
remote:     Note: In UTF-8, the following characters are encoded as follow:
remote:
remote:       â -> "\303\242" == c3 a2  (latin small letter a with circumflex)
remote:       ü -> "\303\274" == c3 bc  (latin small letter u with diaeresis)
remote:       î -> "\303\256" == c3 ae  (latin small letter i with circumflex)
remote:
remote: Diff:
remote: ---
remote:  "M\303\242n\303\274 Scr\303\256pt.txt" | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git "a/M\303\242n\303\274 Scr\303\256pt.txt" "b/M\303\242n\303\274 Scr\303\256pt.txt"
remote: new file mode 100644
remote: index 0000000..3e71550
remote: --- /dev/null
remote: +++ "b/M\303\242n\303\274 Scr\303\256pt.txt"
remote: @@ -0,0 +1 @@
remote: +Some text.
To ../bare/repo.git
   df3425a..58067db  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
