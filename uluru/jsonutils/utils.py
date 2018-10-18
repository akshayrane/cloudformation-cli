from collections.abc import Sequence

from .pointer import fragment_encode


class BaseRefPlaceholder:
    """A sentinel object representing a reference inside the base document."""

    def __repr__(self):
        """Readable representation for debugging.

        >>> repr(BaseRefPlaceholder())
        '<BASE>'
        """
        return "<BASE>"


BASE = BaseRefPlaceholder()


def rewrite_ref(ref):
    """Rewrite a reference to be inside of the base document. A relative JSON
    pointer is returned (in URI fragment identifier representation).

    If the reference is already inside the base document (:ref:`BASE`), the parts
    are simply encoded into a pointer.

    If the reference is outside of the base document, a unique pointer inside
    the base document must be constructed:

    1. the remote parts are flattened into a single, unique part
       (i.e.``/foo/bar`` becomes ``foo~1bar``)
    2. the unique part is namespaced under the remote base name inside the
       definitions section

    The resulting pointer is therefore ``#/definitions/<schema>/<flattened_part>``.

    >>> rewrite_ref((BASE, "foo", "bar"))
    '#/foo/bar'
    >>> rewrite_ref((BASE,))
    '#'
    >>> rewrite_ref(("remote", "foo", "bar"))
    '#/definitions/remote/foo~1bar'
    >>> rewrite_ref(("remote",))
    '#/definitions/remote/'
    """
    base, *parts = ref
    if base is not BASE:
        parts = ["definitions", base, "/".join(parts)]
    return fragment_encode(parts)


def traverse(document, path_parts):
    """Traverse the document according to the reference.

    Since the document is presumed to be the reference's base, the base is
    discarded. There is no validation that the reference is valid.

    :raises ValueError, LookupError: the reference is invalid for this document

    >>> traverse({"foo": {"bar": [42]}}, tuple())
    {'foo': {'bar': [42]}}
    >>> traverse({"foo": {"bar": [42]}}, ["foo"])
    {'bar': [42]}
    >>> traverse({"foo": {"bar": [42]}}, ("foo", "bar"))
    [42]
    >>> traverse({"foo": {"bar": [42]}}, ("foo", "bar", "0"))
    42
    >>> traverse({}, ["foo"])
    Traceback (most recent call last):
    ...
    KeyError: 'foo'
    >>> traverse([], ["foo"])
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 10: 'foo'
    >>> traverse([], [0])
    Traceback (most recent call last):
    ...
    IndexError: list index out of range
    """
    for part in path_parts:
        if isinstance(document, Sequence):
            part = int(part)
        document = document[part]
    return document
