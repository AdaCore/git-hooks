from support import *

class TestRun(TestCase):
    def test_push_notes(testcase):
        cd ('%s/repo' % TEST_DIR)

        # In this testcase, the contents of the emails being sent
        # by the git-hooks is not important, so reduce verbosity at
        # that level to reduce the noise in the hooks' output.

        testcase.change_email_sending_verbosity(full_verbosity=False)

        # First, update the git-hooks configuration to install our
        # the script we want to use as our commit-extra-checker.

        p = Run(['git', 'fetch', 'origin', 'refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'checkout', 'FETCH_HEAD'])
        testcase.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'config', '--file', 'project.config',
                 'hooks.commit-extra-checker',
                 os.path.join(TEST_DIR, 'commit-extra-checker.py')])
        testcase.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'commit', '-m', 'Add hooks.commit-extra-checker',
                 'project.config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        testcase.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        assert 'HEAD -> refs/meta/config' in p.out.splitlines()[-1], p.image

        # Push a couple of notes. We expect the commit-extra-checker
        # to be called on the notes themselves (not on the commits
        # to which the notes are attached).

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/notes/commits 58e8efaaf0dee13edea66b1abbd4b669132b3d77
remote: -----[ stdin ]-----
remote: {"ref_kind": "notes", "body": "Notes added by 'git notes add'", "author_email": "brobecker@adacore.com", "subject": "Notes added by 'git notes add'", "object_type": "commit", "rev": "58e8efaaf0dee13edea66b1abbd4b669132b3d77", "author_name": "Joel Brobecker", "ref_name": "refs/notes/commits"}
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/notes/commits 0892f7e8d41c265fc0ffcbe604f0e7ce784bd9d2
remote: -----[ stdin ]-----
remote: {"ref_kind": "notes", "body": "Notes added by 'git notes add'", "author_email": "brobecker@adacore.com", "subject": "Notes added by 'git notes add'", "object_type": "commit", "rev": "0892f7e8d41c265fc0ffcbe604f0e7ce784bd9d2", "author_name": "Joel Brobecker", "ref_name": "refs/notes/commits"}
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [notes][repo] New file: a....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [notes][repo] Separate subject from body with empty line in file a....
To ../bare/repo.git
   bbcc356..0892f7e  refs/notes/commits -> refs/notes/commits
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # The master branch in our repository has one commit which
        # hasn't been pushed to the remote, yet. Annotate that commit,
        # and try to push that note.
        #
        # In that situation, the git-hooks should refuse the update
        # telling the user to push the commits that are missing first,
        # before pushing the notes. As a result, the commit-extra-checker
        # should not be called at all.

        p = Run(['git', 'notes', 'add', '-m', 'an annotation', 'master'])
        testcase.assertEqual(p.status, 0, p.image)

        p = Run('git show-ref refs/notes/commits'.split())
        testcase.assertEqual(p.status, 0, p.image)
        new_note_sha1 = p.out.split()[0]

        p = Run('git push origin notes/commits'.split())
        expected_out = """\
remote: *** The commit associated to the following notes update
remote: *** cannot be found. Please push your branch commits first
remote: *** and then push your notes commits.
remote: ***
remote: *** Notes commit:     {new_note_sha1}
remote: *** Annotated commit: 4d958ce37f8b04f04e3704ca0786bb5c0ff55f41
remote: ***
remote: *** Notes contents:
remote: *** an annotation
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits -> refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(new_note_sha1=new_note_sha1)

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
