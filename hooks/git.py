# Utility functions for git
#
# Copyright (C) 2008  Owen Taylor
# Copyright (C) 2009  Red Hat, Inc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, If not, see
# http://www.gnu.org/licenses/.
#
# (These are adapted from git-bz)

import os
import re
from subprocess import Popen, PIPE
import sys

def die(message):
    print >>sys.stderr, message
    sys.exit(1)

# Clone of subprocess.CalledProcessError (not in Python 2.4)
class CalledProcessError(Exception):
    def __init__(self, returncode, cmd):
        self.returncode = returncode
        self.cmd = cmd

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

NULL_REVISION = "0000000000000000000000000000000000000000"

# Run a git command
#    Non-keyword arguments are passed verbatim as command line arguments
#    Keyword arguments are turned into command line options
#       <name>=True => --<name>
#       <name>='<str>' => --<name>=<str>
#    Special keyword arguments:
#       _quiet: Discard all output even if an error occurs
#       _interactive: Don't capture stdout and stderr
#       _input=<str>: Feed <str> to stdinin of the command
#       _outfile=<file): Use <file> as the output file descriptor
#       _split_lines: Return an array with one string per returned line
#
def git_run(command, *args, **kwargs):
    to_run = ['git', command.replace("_", "-")]

    interactive = False
    quiet = False
    input = None
    interactive = False
    outfile = None
    do_split_lines = False
    for (k,v) in kwargs.iteritems():
        if k == '_quiet':
            quiet = True
        elif k == '_interactive':
            interactive = True
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

    if outfile:
        stdout = outfile
    else:
        if interactive:
            stdout = None
        else:
            stdout = PIPE

    if interactive:
        stderr = None
    else:
        stderr = PIPE

    if input != None:
        stdin = PIPE
    else:
        stdin = None

    process = Popen(to_run,
                    stdout=stdout, stderr=stderr, stdin=stdin)
    output, error = process.communicate(input)
    if process.returncode != 0:
        if not quiet and not interactive:
            print >>sys.stderr, error,
            print output,
        raise CalledProcessError(process.returncode, " ".join(to_run))

    if interactive or outfile:
        return None
    else:
        if do_split_lines:
            return output.strip().splitlines()
        else:
            return output.strip()

# Wrapper to allow us to do git.<command>(...) instead of git_run()
#
# One difference: The `_outfile' parameter may be a string, in which
# case the output is redirected to that file (if the file is already
# present, it is overwritten).
class Git:
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
    def __init__(self, id, subject):
        self.id = id
        self.subject = subject

# Takes argument like 'git.rev_list()' and returns a list of commit objects
def rev_list_commits(*args, **kwargs):
    kwargs_copy = dict(kwargs)
    kwargs_copy['pretty'] = 'format:%s'
    kwargs_copy['_split_lines'] = True
    lines = git.rev_list(*args, **kwargs_copy)
    if (len(lines) % 2 != 0):
        raise RuntimeException("git rev-list didn't return an even number of lines")

    result = []
    for i in xrange(0, len(lines), 2):
        m = re.match("commit\s+([A-Fa-f0-9]+)", lines[i])
        if not m:
            raise RuntimeException("Can't parse commit it '%s'", lines[i])
        commit_id = m.group(1)
        subject = lines[i + 1]
        result.append(GitCommit(commit_id, subject))

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


# Loads a single commit object by ID
def load_commit(commit_id):
    return rev_list_commits(commit_id + "^!")[0]

# Return True if the commit has multiple parents
def commit_is_merge(commit):
    if isinstance(commit, basestring):
        commit = load_commit(commit)

    parent_count = 0
    for line in git.cat_file("commit", commit.id, _split_lines=True):
        if line == "":
            break
        if line.startswith("parent "):
            parent_count += 1

    return parent_count > 1

# Return a short one-line summary of the commit
def commit_oneline(commit):
    if isinstance(commit, basestring):
        commit = load_commit(commit)

    return commit.id[0:7]+"... " + commit.subject[0:59]

# Return the directory name with .git stripped as a short identifier
# for the module
def get_module_name():
    try:
        git_dir = git.rev_parse(git_dir=True, _quiet=True)
    except CalledProcessError:
        die("GIT_DIR not set")

    # Use the directory name with .git stripped as a short identifier
    absdir = os.path.abspath(git_dir)
    if absdir.endswith(os.sep + '.git'):
        absdir = os.path.dirname(absdir)
    projectshort = os.path.basename(absdir)
    if projectshort.endswith(".git"):
        projectshort = projectshort[:-4]

    return projectshort

# Return the project description or '' if it is 'Unnamed repository;'
def get_project_description():
    try:
        git_dir = git.rev_parse(git_dir=True, _quiet=True)
    except CalledProcessError:
        die("GIT_DIR not set")

    projectdesc = ''
    description = os.path.join(git_dir, 'description')
    if os.path.exists(description):
        try:
            projectdesc = open(description).read().strip()
        except:
            pass
    if projectdesc.startswith('Unnamed repository;'):
        projectdesc = ''

    return projectdesc


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
        git.cat_file('-e', '%s:%s' % (commit_rev, filename), _quiet=True)
    except CalledProcessError:
        # cat-file -e returned non-zero; the file does not exist.
        return False
    return True
