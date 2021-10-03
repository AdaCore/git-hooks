"""A module to determine file attribute values at any commit.

This code could logically belong in git.py, but it is kept here instead,
because it makes some assumptions that are specific to AdaCore (Eg:
we take into account a default_attributes file in info/).
"""

import os
from os.path import isfile
from shutil import copy

from git import git, file_exists
from io_utils import encode_utf8
from tempfile import mkdtemp
import utils

# The name of the default attributes file in the bare repository.
# This file expected to be relative to the root of the bare repository.
DEFAULT_ATTRIBUTES_FILE = "info/default_attributes"


def cached_file_exists(commit_rev, filename):
    """A wrapper around git.file_exists but with a cache...

    ... to avoid repetitive calls to git.

    PARAMETERS
        commit_rev: Same as git.file_exists.
        filename: Same as git.file_exists.
    """
    # Implement the cache as an attribute of this function,
    # where the key is a tuple (commit_rev, filename), and
    # the value the result of the query.
    if "cache" not in cached_file_exists.__dict__:
        # First time call, initialize the attribute.
        cached_file_exists.cache = {}

    key = (commit_rev, filename)
    if key not in cached_file_exists.cache:
        cached_file_exists.cache[key] = file_exists(commit_rev, filename)
    return cached_file_exists.cache[key]


def git_attribute(commit_rev, filename_list, attr_name):
    """Return filename's attribute value at commit_rev.

    PARAMETERS
        commit_rev: The commit to use in order to determine the
            attribute value.  This is important, because more recent
            commits may have changed the attribute value through
            updates of various .gitattributes files.
        filename_list: A list of filenames for which the attribute is
            to be determined.  The file name should be relative to
            the root of the repository.
        attr_name: The name of the attribute.

    RETURN VALUE
        A dictionary, where the key is a the filename (one key for
        each file in filename_list), and the value is the file's
        attribute value as returned by git (Eg. 'set', 'unset',
        'unspecified', etc).

    REMARKS
        The problem is not as easy as it looks.  If we were working
        from a full (non-bare) repository, the `git check-attr'
        command would give us our answer immediately.  But in bare
        repositories, the only file read is GIT_DIR/info/attributes.

        Originally, we implemented this way: Starting from the directory
        where our file is located, find the first .gitattribute file
        that specifies an attribute value for our file.  Unfortunately,
        reading the gitattributes(5) man page more careful, we realized
        that this does not implement gitattributes semantics properly
        (we don't stop once we found a .gitattributes file with an entry
        that matches). Also, this approach turned out to be extremely
        slow, and could cause some updates to take minutes to process
        for commits where 2-3 thousand files were modified (typical
        when updating the copyright year, for instance).

        So, instead of trying to re-implement the git-check-attr
        command ourselves, what we do now, is create a dummy git
        repository inside which we (lazily) reproduce the directory
        tree, with their .gitattributes file. And then, from there
        call `git check-attr'. And, to help with the performance
        aspect, we call it only once requesting the attribute value
        for all files all in one go.
    """
    # Verify that we have a scratch area we can use for create the fake
    # git repository (see REMARKS section above).
    assert utils.scratch_dir is not None

    # A copy of the environment, but without the GIT_DIR environment
    # variable (which gets sets when called by git), pointing to
    # the repository to which changes are being pushed.  This interferes
    # with most git commands when we're trying to work with our fake
    # repository. So we use this copy of the environment without
    # the GIT_DIR environment variable when needed.
    tmp_git_dir_env = dict(os.environ)
    tmp_git_dir_env.pop("GIT_DIR", None)

    tmp_git_dir = mkdtemp(".git", "check-attr-", utils.scratch_dir)
    git.init(_cwd=tmp_git_dir, _env=tmp_git_dir_env)

    # There is one extra complication: We want to also provide support
    # for a DEFAULT_ATTRIBUTES_FILE, where the semantics is that,
    # if none of the .gitattributes file have an entry matching
    # our file, then this file is consulted. Once again, to avoid
    # calling `git check-attr' multiple times, what we do instead
    # is that we create a the directory tree in a root which is in
    # a subdir of tmp_git_dir. That way, we can put the default
    # attribute file in the root of tmp_git_dir, and git-check-attr
    # will only look at it if checked-in .gitattributes don't define
    # the attribute of a given file, thus implementing the "default"
    # behavior.
    #
    # This requires a bit of manipulation, because now, in the fake
    # git repository, the files we want to check are conceptually
    # inside the subdir.  So filenames passed to `git check-attr'
    # have to contain that subdir, and the that subdir needs to be
    # excised from the command's output.

    if isfile(DEFAULT_ATTRIBUTES_FILE):
        copy(DEFAULT_ATTRIBUTES_FILE, os.path.join(tmp_git_dir, ".gitattributes"))
    checkout_subdir = "src"
    tmp_checkout_dir = os.path.join(tmp_git_dir, checkout_subdir)

    dirs_with_changes = {}
    for filename in filename_list:
        assert not os.path.isabs(filename)
        dir_path = filename
        dir_created = False
        while dir_path:
            dir_path = os.path.dirname(dir_path)
            if dir_path in dirs_with_changes:
                continue
            gitattributes_rel_file = os.path.join(dir_path, ".gitattributes")
            if cached_file_exists(commit_rev, gitattributes_rel_file):
                if not dir_created:
                    os.makedirs(os.path.join(tmp_checkout_dir, dir_path))
                    dir_created = True
                git.show(
                    "%s:%s" % (commit_rev, gitattributes_rel_file),
                    _outfile=os.path.join(tmp_checkout_dir, gitattributes_rel_file),
                )
            dirs_with_changes[dir_path] = True

    # To avoid having to deal with the parsing of quoted filenames,
    # we use the -z option of "git check-attr". What this does is
    # that each of the 3 elements of each line is now separated by
    # a NUL character. Also, each line now ends with a NUL character
    # as well, instead of LF.
    #
    # To parse the output, we split it at each NUL character.
    # This means that the output gets split into a sequence of
    # lines which go 3 by 3, with the first line containing
    # the filename, the second being the name of the attribute
    # being queried, and the third being the attribute's value
    # for that file.
    check_attr_input = "\x00".join(
        ["%s/%s" % (checkout_subdir, filename) for filename in filename_list]
    )
    attr_info = git.check_attr(
        "-z",
        "--stdin",
        attr_name,
        _cwd=tmp_git_dir,
        _env=tmp_git_dir_env,
        _input=encode_utf8(check_attr_input),
        _decode=True,
    ).split("\x00")
    if len(attr_info) % 3 == 1 and not attr_info[-1]:
        # The attribute information for each filename ends with
        # a NUL character, so the terminating NUL character in
        # the last entry caused the split to add one empty element
        # at the end. This is expected, so just remove it.
        attr_info.pop()

    # As per the above, we should now have a number of lines that's
    # a multiple of 3.
    assert len(attr_info) % 3 == 0

    result = {}
    while attr_info:
        filename = attr_info.pop(0)
        attr_info.pop(0)  # Ignore the attribute name...
        attr_val = attr_info.pop(0)

        assert filename.startswith(checkout_subdir + "/")
        filename = filename[len(checkout_subdir) + 1 :]

        result[filename] = attr_val

    return result
