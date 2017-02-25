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
           _cwd=<str>: Run the git command from the given directory.
           _env=<dict>: Same as the "env" parameter of the Popen constructor.
           _input=<str>: Feed <str> to stdinin of the command
           _outfile=<file): Use <file> as the output file descriptor
           _split_lines: Return an array with one string per returned line
    """
    to_run = ['git', command.replace("_", "-")]

    cwd = None
    env = None
    input = None
    outfile = None
    do_split_lines = False
    for (k, v) in kwargs.iteritems():
        if k == '_cwd':
            cwd = v
        elif k == '_env':
            env = v
        elif k == '_input':
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

    process = Popen(to_run, stdout=stdout, stderr=STDOUT, stdin=stdin,
                    cwd=cwd, env=env)
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
                if (('_outfile' in kwargs and
                     isinstance(kwargs['_outfile'], basestring))):
                    tmp_fd = open(kwargs['_outfile'], 'w')
                    kwargs['_outfile'] = tmp_fd
                return git_run(command, *args, **kwargs)
            finally:
                if tmp_fd is not None:
                    tmp_fd.close()
        return f


git = Git()


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


def is_null_rev(rev):
    """Return True iff rev is the a NULL commit SHA1.
    """
    return re.match("0+$", rev) is not None


def empty_tree_rev():
    """Return the empty tree's SHA1.

    This is a SHA1 one can use as the parent of a commit that
    does not have a parent (root commit).
    """
    # To compute this SHA1 requires a call to git, so cache
    # the result in an attribute called 'cached_rev'.
    if not hasattr(empty_tree_rev, 'cached_rev'):
        empty_tree_rev.cached_rev = git.mktree(_input='')
    return empty_tree_rev.cached_rev


def is_valid_commit(rev):
    """Return True if rev is a valid commit.

    PARAMETERS
        rev: The commit SHA1 we want to test.
    """
    try:
        git.cat_file('-e', rev)
        return True
    except CalledProcessError:
        return False


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


def commit_rev(rev):
    """Resolve rev into a commit revision (SHA1).

    For commit revs, this is a no-op.  But of other types of revisions
    (such as a tag, for instance), this resolves the tag into the actual
    object it points to.

    PARAMETERS
        rev: A revision.
    """
    return git.rev_list('-n1', rev)


def commit_oneline(rev):
    """Return a short one-line summary of the commit.

    PARAMETERS
        rev: A commit revision (SHA1).
    """
    info = git.rev_list(rev, max_count='1', oneline=True)
    (short_rev, subject) = info.split(None, 1)
    return "%s... %s" % (short_rev, subject[0:59])


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
    result = {'tagger':   '*** Failed to determine tagger ***',
              'date':     '*** Failed to determine tag creation date ***',
              'signed_p': False}

    # We used to be able to extract everything we need about the tag
    # from the output of "git cat-file -p". Unfortunately, at least
    # as of git version 1.8.3.2, the date is no longer pretty-printed,
    # giving us now a timestamp and a TZ (Eg: '1340722274 -0700')
    # instead of a human-readable date (Eg: 'Tue Jun 26 07:51:14 2012
    # -0700').
    #
    # This seems to be a deliberate change, and attempts to find
    # a way to either get git to pretty-print that timestamp have
    # failed. Attempts to convert that timestamp ourselves have
    # also failed; in the example above we get a translation which
    # appears to be off by an odd number of hours: '18:51:14 -0700'
    # instead of '07:51:14 -0700'. The difference of 11 hours is
    # odd.
    #
    # After having wasted a certain amount of time, it seems to me
    # that the only practical solution is to get git to pretty-print
    # the timestamp. The only way I found to inspect the tag itself
    # was via "git show". "git show" prints the tagger and date fine,
    # as well as the tag's revision log.  But it follows the tag
    # description with a description of the tagged commit (the same
    # we'd get if we did "git show" of that commit).  That part makes
    # the extraction of the tag's revision log a little harder.
    # On top of that, trying to touch the output via the --format
    # command-line option in order to facilitate a bit the parsing
    # immediately results in the "Date:" field disappearing from
    # the tag section! ARGH!
    #
    # Rather than add more heuristics about how the commit's section
    # starts, we'll limit the extract from the output of "git show"
    # to the tagger and date fields only. And we will overcome the
    # rev-log/signature extraction issue by calling "git cat-file"
    # (as we used to do before).

    for line in git.show(tag_name, _split_lines=True):
        if line.strip() == '':
            break
        elif line.startswith('Tagger:'):
            result['tagger'] = line.partition(':')[2].strip()
        elif line.startswith('Date:'):
            result['date'] = line.partition(':')[2].strip()

    # Now, get the revision log using "git cat-file -p".
    #
    # The first section contains information about the tag, such as
    # the tag name, type, and tagger.  We have already collected
    # that information above, so skip it (we know that it ends with
    # an empty line).
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

    This function assumes that all arguments are valid, and
    the usual CalledProcessError will be raised if not.

    PARAMETERS
        *args: Each argument is passed to the "git show-ref"
            as a pattern.

    RETURN VALUE
        A dictionary of references that matched the given patterns,
        minus the references matching the hooks.ignore-refs config.
    """
    # We cannot import that at module level, because module config
    # actually depends on this module.  So we import it here instead.
    from config import git_config

    matching_refs = git.show_ref(*args, _split_lines=True)
    result = {}
    for ref_info in matching_refs:
        rev, ref = ref_info.split(None, 2)
        result[ref] = rev

    # Remove all references which matching the hooks.ignore-refs config.
    #
    # It would probably have been more efficient to check the reference
    # against the exclusion list before adding them to the dictionary.
    # I felt that the resulting code was harder to read.  Given the
    # typical number of entries, the impact should be barely measurable.
    ignore_refs_list = [regex.strip()
                        for regex in git_config('hooks.ignore-refs')]

    for ref_name in result.keys():
        for ignore_ref_re in ignore_refs_list:
            if re.match(ignore_ref_re, ref_name):
                del result[ref_name]
                break

    return result


def commit_parents(rev):
    """Return the commit parents.

    PARAMETERS
        rev: The revision for which the parents need to be computed.

    RETURN VALUE
        A list of revisions corresponding to each parent, ordered
        (ie: the first parent is first on the list, etc). If this is
        a headeless commit, return an empty list.
    """
    return git.log('-n1', '--pretty=format:%P', rev).strip().split()


def commit_subject(rev):
    """Return the commit's subject.

    PARAMETERS
        rev: A commit revision.
    """
    info = git.rev_list(rev, max_count='1', oneline=True)
    _, subject = info.split(None, 1)
    return subject


def diff_tree(*args, **kwargs):
    """Same as git.diff_tree, but handling weird filenames properly.

    When the diff-tree output lists some files whose name contain
    some unusual characters (double-quote, tabs, newlines, backslashes),
    the filename is quoted, and those special characters are
    escaped. This function provides an interface to "git diff-tree"
    which handles everything.

    PARAMETERS
        Same as with git.diff_tree.
        *** NOTE *** Do not use _split_lines. It is useless in this case,
            and would likely interfere with this implementation.

    RETURN VALUE
        A list, with one element per file modified. Each element
        is a 6-element tuple, organized as follow:
            (old_mode, new_mode, old_sha1, new_sha1, status, filename)
    """
    assert '_split_lines' not in kwargs, \
        'git.py::diff_tree should never be called with _split_lines'

    # To avoid having to deal with the parsing of quoted filenames,
    # we use the -z option of "git diff-tree". What this does is
    # that it separates the filename from the rest of the data
    # using the NUL character instead of a space or newline.
    #
    # To parse the output, we split it at each NUL character.
    # This means that the output gets split into a sequence of
    # pairs of lines, with the first line containing the information
    # about a given file, and the line following it containing
    # the name of the file.
    diff_data = git.diff_tree('-z', *args, **kwargs).split('\x00')

    # When doing a "git diff-tree" with a single tree-ish, the output
    # starts with the hash of what is being compared. We're not
    # interested in this piece of information, so strip it.
    if diff_data and diff_data[0] and not diff_data[0].startswith(':'):
        assert re.match('[0-9a-fA-F]+$', diff_data[0]) is not None
        diff_data.pop(0)

    if len(diff_data) % 2 == 1 and not diff_data[-1]:
        # Each filename ends with a NUL character, so the terminating
        # NUL character in the last entry caused the split to add
        # one empty element at the end. This is expected, so just
        # remove it.
        diff_data.pop()

    # As per the above, we should now have an even number of elements
    # in our list.
    assert len(diff_data) % 2 == 0

    result = []
    while diff_data:
        stats = diff_data.pop(0)
        filename = diff_data.pop(0)

        # The stats line should start with a colon and then be followed
        # by space-separated information about the changes made to our
        # file.  Strip that colon before we do the splitting.
        assert stats.startswith(':')
        stats = stats[1:]

        (old_mode, new_mode, old_sha1, new_sha1, status) = stats.split(None, 4)
        result.append((old_mode, new_mode, old_sha1, new_sha1, status,
                       filename))

    return result
