# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Some compatibility support for different python versions.'''

from __future__ import absolute_import

import sys
import types


try:
    # Try six module.
    from six import (
        PY2,
        PY3,
        string_types,
        integer_types,
        class_types,
        text_type,
        binary_type,
        _add_doc,
    )

except ImportError:
    # Some py2/py3 compatibility support based on a stripped down version of six.
    PY2 = sys.version_info[0] == 2
    PY3 = sys.version_info[0] == 3

    if not PY2:
        string_types = (str,)
        integer_types = (int,)
        class_types = (type,)
        text_type = str
        binary_type = bytes
    else:
        string_types = (basestring,)
        integer_types = (int, long)
        class_types = (type, types.ClassType)
        text_type = unicode
        binary_type = str

    def _add_doc(func, doc):
        '''Add documentation to a function.'''
        func.__doc__ = doc

# xb and xu are different from b and u in six.
# Code without 2.5 support does not need xb().
# Code that only supports Python 3 versions greater than 3.3 thus does not need xu().
if not PY2:
    def xb(string):
        return string.encode('utf-8')
    def xu(string):
        return string
else:
    def xb(string):
        return string.encode('utf-8') if isinstance(string, unicode) else string
    def xu(string):
        return string if isinstance(string, unicode) else unicode(string, 'utf-8')
_add_doc(xb, '''Byte literal''')
_add_doc(xu, '''Text literal''')


try:
    _bytearray = bytearray      # New in version 2.6.
except NameError:
    _bytearray = type(None)
try:
    _memoryview = memoryview    # New in version 2.7.
except NameError:
    _memoryview = type(None)


def force_bytes(value, encoding='utf-8', errors='strict'):
    '''Force value to bytes.'''
    if isinstance(value, binary_type):
        return value
    if isinstance(value, string_types):
        return value.encode(encoding, errors)
    if not isinstance(value, type(None)) and isinstance(value, _memoryview):
        return value.tobytes()
    return binary_type(value) if PY2 else text_type(value).encode(encoding, errors)


def force_text(value, encoding='utf-8', errors='strict'):
    '''Force value to text.'''
    if isinstance(value, text_type):
        return value
    if not isinstance(value, type(None)) and isinstance(value, (binary_type, _bytearray)):
        return value.decode(encoding, errors)
    if hasattr(value, '__unicode__'):
        return value.__unicode__()
    return text_type(value) if not PY2 else str(value).decode(encoding, errors)


def _getwriter(encoding):
    '''Return a :class:`codecs.StreamWriter` that resists tracing back.

    @ref kitchen.text.converters.getwriter
    @see https://pythonhosted.org/kitchen/unicode-frustrations.html
    '''
    import codecs

    class _StreamWriter(codecs.StreamWriter):
        '''Stream writer be able to print unicode.'''
        def __init__(self, stream, errors='strict'):
            codecs.StreamWriter.__init__(self, stream, errors)

        def encode(self, input, errors='strict'):
            return (force_bytes(input, encoding=self.encoding, errors=errors), len(input))

    _StreamWriter.encoding = encoding
    return _StreamWriter


_UNICODE_PRINT = False

def unicode_print():
    '''Setup sys.stdout and sys.stderr for unicode print in python 2.'''
    if PY2:
        global _UNICODE_PRINT
        if not _UNICODE_PRINT:
            _UNICODE_PRINT = True
            sys.stdout = _getwriter('utf-8')(sys.stdout)
            sys.stderr = _getwriter('utf-8')(sys.stderr)
