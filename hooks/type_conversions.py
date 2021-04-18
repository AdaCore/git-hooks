"""A number of utility functions performing type conversions...
"""


def to_bool(val):
    """Translate val into a either True or False.

    Raise ValueError if val cannot be converted.

    PARAMETERS
        val: The value to convert.  It can be either a boolean,
            in which case this function is a no-op, or a string
            whose (lowercase) value must then be either 'true'
            or 'false'.

    REMARKS
        It would be nice if we could have used the bool builtin
        function, but this function unfortunately returns something
        different: It applies the truth test on the argument, and
        then returns the result of that test.  In other words,
        bool("False") returns True!
    """
    if val in (True, False):
        return val
    val_str = str(val).lower()
    if val_str == 'true':
        return True
    if val_str == 'false':
        return False
    raise ValueError("invalid boolean value: '%s'", str(val))


def to_tuple(val):
    """Translate val into a tuple.

    PARAMETERS
        val: The value to convert, assumed to be a string for now.
            An assertion will be raised if this is not the case.

    REMARKS
        Handling of val being a tuple, or even maybe other types
        could be added as well.  But there is no need for it at
        the moment.
    """
    assert isinstance(val, str)

    # Handle the case where val is empty separately, as split would
    # return a tuple containing an empty string.  We want to return
    # an empty tuple in this case.
    if not val:
        return ()
    return tuple(val.split(','))


def to_type(val, new_type):
    """Translate val to the given type.

    Raise ValueError if val cannot be converted.

    PARAMETERS
        val: The value to convert.
        new_type: A callable that indicates the new type for the value.
            Usually one of the built-in functions such as 'int', or
            'bool', etc.
    """
    # Most of the built-ins perform a translation job, but there
    # are some exceptions...
    if new_type == bool:
        new_type = to_bool
    elif new_type == tuple:
        new_type = to_tuple
    return new_type(val)
