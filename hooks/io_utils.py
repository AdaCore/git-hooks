import sys


def safe_decode(b):
    """Decode the given byte string after trying to guess the encoding...

    This function tries to decode the given byte string by guessing
    the encoding. Guessing is not ideal, but is often necessary when
    trying to decode some output obtained from running some external
    program. For instance, it is not always possible to tell in advance
    or force what encoding the output from a Git command might be.
    So this function simply tries a few of the more widely used encodings
    until one works.

    Note that the encoding that this function tries last is the iso-8859-15
    encoding. We try it last, because Python (at least as of version 3.8)
    is always successful in decoding any byte using that encoding, as
    demonstrated by the following statement completing successfully:

        bytes(range(256)).decode("iso-8859-15")

    This is a bit unexpected, considering the fact that the range [A0..9F]
    is not defined in that encoding. But this doesn't seem to be a problem,
    even when trying to re-encode the obtained string with UTF-8, something
    we are likely to do if we want to display the information to the user.

    What this means is that this function will always be successful in
    converting the given byte string into a string. Should it happen
    one day that the last encoding not be able to decode any sequence,
    we'll probably want to add a decoder where unknown sequences are
    replaced by an escaped value.

    PARAMETERS
        b: A byte string to convert.

    RETURN VALUE
        A unicode string.
    """
    for potential_encoding in (
        # The most popular encoding, by far, and also the encoding that
        # Git itself uses in some cases (e.g. storing path names), is UTF-8.
        # Try that first.
        "UTF-8",
        # Finally, the iso-8859-15; try this one last, as explained in
        # the function's documentation above (this one will always succeed).
        "iso-8859-15",
    ):
        try:
            return b.decode(potential_encoding)
        except UnicodeDecodeError:
            pass


def safe_decode_by_line(b):
    """Same as safe_decode, but doing the decoding line by line.

    This can be useful to decode the output from commands where the encoding
    may change from line to line. It might be surprising to hear that, but
    we have seen this happen when using some Git commands that concatenate
    output from multiple sources with possibly different encodings.

    What this function does is split the output in lines, and decodes each line
    using safe_decode -- this makes the assumption that there is no encoding
    change mid-line, but that seems very unlikely, and so we will not try
    to support this scenario (if this happens with a Git command, we'll try
    to re-craft it so as to make sure the assumption is met).

    PARAMETERS
        b: A byte string to convert.

    RETURN VALUE
        A unicode string.
    """
    return "\n".join(safe_decode(line) for line in b.splitlines())


def encode_utf8(s):
    """Return s.encode("UTF-8") if running with Python 3.x, else return s.

    This function is here to help us prepare for the transition to
    Python 3.x, where strings that we want to write or pass to another
    process need to be converted to bytes, while at the same time
    retaining the current behavior when running with Python 2.x
    (pass the string as is, without any transformation).

    This is therefore a temporary function that we should get rid of
    as soon as we stop supporting Python 2.x (FIXME).

    PARAMETERS
        s: A string to be encoded.

    RETURN VALUE
        A byte string.
    """
    if sys.version_info[0] < 3:
        return s  # pragma: py2-only
    else:  # pragma: py3-only
        return s.encode("UTF-8")
