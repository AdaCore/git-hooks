# Utility functions for git
#
# Derived in a very large part from the gnome git hooks, themselves
# apparently adapted form git-bz.
#
# Original copyright header:
#
# | Copyright (C) 2008  Owen Taylor
# | Copyright (C) 2009  Red Hat, Inc
# |
# | This program is free software; you can redistribute it and/or
# | modify it under the terms of the GNU General Public License
# | as published by the Free Software Foundation; either version 2
# | of the License, or (at your option) any later version.
# |
# | This program is distributed in the hope that it will be useful,
# | but WITHOUT ANY WARRANTY; without even the implied warranty of
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# | GNU General Public License for more details.
# |
# | You should have received a copy of the GNU General Public License
# | along with this program; if not, If not, see
# | http://www.gnu.org/licenses/.
# |
# | (These are adapted from git-bz)

import os
import re
from subprocess import Popen, PIPE, STDOUT
import subprocess
import sys


class CalledProcessError(subprocess.CalledProcessError):
    """An exception raised in case of failure in this module.
    """
    # Initially, defining this exception here was a way to shield
    # the script from the fact that subprocess.CalledProcessError
    # is not defined in Python 2.4.  So the exception was simply
    # a clone of the exception defined in subprocess.
    #
    # But we now require Python 2.7 or later, so this exception
    # is now guarantied to be available.  However, for convenience
    # of use (users of this module then need not import symbols from
    # module subprocess), make that class an identical child.
    pass

def git_run(command, *args, **kwargs):
    """Run a git command.

    PARAMETERS
        Non-keyword arguments are passed verbatim as command line arguments
        Keyword arguments are turned into command line options
           <name>=True => --<name>
           <name>='<str>' => --<name>=<str>
        Special keyword arguments:
           _input=<str>: Feed <str> to stdinin of the command
           _outfile=<file): Use <file> as the output file descriptor
           _split_lines: Return an array with one string per returned line
    """
    to_run = ['git', command.replace("_", "-")]

    input = None
    outfile = None
    do_split_lines = False
    for (k,v) in kwargs.iteritems():
        if k == '_input':
            input = v
        elif k == '_outfile':
            outfile = v
        elif k == '_split_lines':
            do_split_lines = True
        elif v is True:
            if len(k) == 1:
                to_run.append("-" + k)
            else:
                to_run.append("--" + k.replace("_", "-"))
        else:
            to_run.append("--" + k.replace("_", "-") + "=" + v)

    to_run.extend(args)

    stdout = outfile if outfile else PIPE
    stdin = None if input is None else PIPE

    process = Popen(to_run, stdout=stdout, stderr=STDOUT, stdin=stdin)
    output, error = process.communicate(input)
    # We redirected stderr to the same fd as stdout, so error should
    # not contain anything.
    assert not error

    if process.returncode != 0:
        raise CalledProcessError(process.returncode,
                                 " ".join(to_run),
                                 output)

    if outfile:
        return None
    else:
        if do_split_lines:
            return output.strip().splitlines()
        else:
            return output.strip()


class Git:
    """Wrapper to allow us to do git.<command>(...) instead of git_run()

    One difference: The `_outfile' parameter may be a string, in which
    case the output is redirected to that file (if the file is already
    present, it is overwritten).
    """
    def __getattr__(self, command):
        def f(*args, **kwargs):
            try:
                # If a string _outfile parameter was given, turn it
                # into a file descriptor.
                tmp_fd = None
                if ('_outfile' in kwargs
                    and isinstance(kwargs['_outfile'], basestring)):
                    tmp_fd = open(kwargs['_outfile'], 'w')
                    kwargs['_outfile'] = tmp_fd
                return git_run(command, *args, **kwargs)
            finally:
                if tmp_fd is not None:
                    tmp_fd.close()
        return f


git = Git()


class GitCommit:
    """A git commit.

    ATTRIBUTES
        rev: The commit's revision (SHA1).
        subject: The subject of the commit.
    """
    def __init__(self, rev, subject):
        """The constructor.

        PARAMETERS
            rev: Same as the attribute.
            subject: Same as the attribute.
        """
        self.rev = rev
        self.subject = subject


def get_git_dir():
    """Return the full path to the repository's .git directory.

    This function is just a convenient short-cut for running
    "git rev-parse --git-dir", with an abspath call added to make
    sure that the returned path is always absolute.

    REMARK
        For bare repositories, there is no .git/ subdirectory.
        In that case, the function returns the equivalent, which
        is the path of the repository itself.
    """
    # Note: The abspath call seems to be needed when calling
    # git either from the repository root dir (in which case
    # it returns either '.' or '.git' depending on whether
    # this is a bare repository or not), or when calling it
    # from the .git directory itself (in which case it returns
    # '.').
    return os.path.abspath(git.rev_parse(git_dir=True))


def rev_list_commits(*args, **kwargs):
    """Run the "git rev-list" command with the given arguments.

    PARAMETERS
        Same principles as with the git_run function.

    RETURN VALUE
        A list GitCommit objects.
    """
    kwargs_copy = dict(kwargs)
    kwargs_copy['pretty'] = 'format:%s'
    kwargs_copy['_split_lines'] = True
    lines = git.rev_list(*args, **kwargs_copy)

    # Given the format string we used, there should be an even number
    # of lines.
    assert len(lines) % 2 == 0

    result = []
    for i in xrange(0, len(lines), 2):
        m = re.match("commit\s+([A-Fa-f0-9]+)", lines[i])
        if not m: # pragma: no cover (should be impossible)
            raise RuntimeException("Can't parse commit it '%s'", lines[i])
        commit_rev = m.group(1)
        subject = lines[i + 1]
        result.append(GitCommit(commit_rev, subject))

    return result


def is_null_rev(rev):
    """Return True iff rev is the a NULL commit SHA1.
    """
    return re.match("0+$", rev) is not None


def get_object_type(rev):
    """Determine the object type of the given commit.

    PARAMETERS
        rev: The commit SHA1 that we want to inspect.

    RETURN VALUE
        The string returned by "git cat-file -t REV", or else "delete"
        if REV is a null SHA1 (all zeroes).
    """
    if is_null_rev(rev):
        rev_type = "delete"
    else:
        rev_type = git.cat_file(rev, t=True)
    return rev_type


def load_commit(commit_id):
    """Return a GitCommit object associated to the given commit_id.

    PARAMETERS
        commit_id: A commit ID (SHA1).
    """
    return rev_list_commits(commit_id + "^!")[0]


def commit_oneline(commit):
    """Return a short one-line summary of the commit.

    PARAMETERS
        commit: A GitCommit object, or a string providing the commit's
            ID (sha1).
    """
    if isinstance(commit, basestring):
        commit = load_commit(commit)
    return commit.rev[0:7]+"... " + commit.subject[0:59]


def get_module_name():
    """Return a short identifer name for the git repository.

    The identifier name is determined using the directory name where
    the git repository is stored, with the .git suffix stripped.
    """
    absdir = get_git_dir()
    if absdir.endswith(os.sep + '.git'):
        absdir = os.path.dirname(absdir)
    projectshort = os.path.basename(absdir)
    if projectshort.endswith(".git"):
        projectshort = projectshort[:-4]

    return projectshort


def file_exists(commit_rev, filename):
    """Return True if a file exists for a given commit.

    PARAMETERS
        commit_rev: The commit to inspect.
        filename: The filename to search for in the given commit_rev.
            The file name must be relative to the repository's root dir.

    RETURN VALUE
        A boolean.
    """
    try:
        git.cat_file('-e', '%s:%s' % (commit_rev, filename))
    except CalledProcessError:
        # cat-file -e returned non-zero; the file does not exist.
        return False
    return True


def parse_tag_object(tag_name):
    """Return a dictionary providing info on an annotated tag.

    The behavior of this function is undefined if tag_name is not
    a valid annotated tag.

    PARAMETERS
        tag_name: The name of the tag. It can be the "short" tag name
            (Eg: "some-tag"), or the reference name (/refs/tags/some-tag,
            for instance).

    RETURN VALUE
        A dictionary with the following keys:
            'tagger': The name of the user who created the tag.
            'date': The date the tag was created.
            'message': The revision log used when creating the tag.
            'signed_p': True if the tag was signed, False otherwise.
    """
    # Provide default values for certain fields.
    result = {'tagger'   : '*** Failed to determine tagger ***',
              'date'     : '*** Failed to determine tag creation date ***',
              'signed_p' : False}

    # Use cat-file -p to dump the contents of the tag.  The output
    # is made of 2 sections, separated by an empty line.
    #
    # The first section contains information about the tag, such as
    # the tag name, type, and tagger.  We're looking for the line
    # that starts with "tagger", as it contains both the name of
    # the tagger as well as the date the message was tagged.
    #
    # The second section contains the revision history, optionally
    # followed by the PGP signature (if the tag was signed).

    revision_log = []
    section_no = 1

    for line in git.cat_file(tag_name, p=True, _split_lines=True):
        if section_no == 1:
            if line.strip() == "":
                # We have reached the end of this section, moving on
                # to the next.
                section_no += 1
                continue
            # Check if the line is the "tagger line", and extract
            # the tagger name and tagging time as best we can.
            m = re.match(r"tagger\s+([^>]*>)\s*(.*)", line)
            if m:
                result['tagger'] = m.group(1)
                result['date'] = m.group(2)
                continue
        else:
            if line.startswith('-----BEGIN PGP SIGNATURE-----'):
                result['signed_p'] = True
                # We don't want to include the PGP signature in
                # the message, and we know there isn't anything else
                # after the PGP signature, so we're done.
                break
            revision_log.append(line)
    result['message'] = "\n".join(["    " + line for line in revision_log])

    return result


def git_show_ref(*args):
    """Call "git show-ref [args]" and return the result as a dictionary.

    The key of the dictionary is the reference name, and the value
    is a string containing the reference's rev (SHA1).

    PARAMETERS
        *args: Each argument is passed to the "git show-ref"
            as a pattern.

    RETURN VALUE
        A dictionary of references that matched the given patterns.
    """
    try:
        matching_refs = git.show_ref(*args, _split_lines=True)
        result = {}
        for ref_info in matching_refs:
            rev, ref = ref_info.split(None, 2)
            result[ref] = rev
        return result
    except CalledProcessError:
        return None
