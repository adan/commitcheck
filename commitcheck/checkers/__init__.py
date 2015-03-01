# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Generic check logic.'''

from __future__ import absolute_import, division, print_function, with_statement

from collections import namedtuple
import re
import sys

from .._compat import force_text


Pattern = namedtuple('Pattern', ['pattern', 'name', 'description'])


class Enum(set):
    '''Simple enumeration.'''
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


CheckTypes = Enum([
    'CHECK_TYPE_GIT_DIFF',
    'CHECK_TYPE_GIT_STAGED',
    'CHECK_TYPE_GIT_TREE',
])


class LineCounter(object):
    '''Generic line counter.'''
    def count_line(self, line):
        '''Returns False if just line numbers line.'''
        raise NotImplementedError

    @property
    def line_number(self):
        '''Returns current line number.'''
        raise NotImplementedError


class BaseChecker(object):
    '''Generic checker.'''
    def __init__(self, ignores=None, checks=None):
        self.verbose = False
        self.ignores = ignores
        self.ignore_patterns = [re.compile(force_text(i)) for i in ignores] if ignores else []
        self.checks = checks
        self.check_patterns = [re.compile(force_text(c)) for c in checks] if checks else []
        self.unexpected_patterns = []
        # Matched pattern names
        self.matched_patterns = set()

    def output(self, value, *args, **kwargs):
        '''Print value.'''
        print(value, *args, **kwargs)

    def verbose_output(self, value, *args, **kwargs):
        '''Print value if verbose.'''
        if self.verbose:
            self.output(value, *args, **kwargs)

    def need_check(self, path):
        '''Returns True if need to check this path.'''
        for pattern in self.ignore_patterns:
            if pattern.match(path):
                return False
        for pattern in self.check_patterns:
            if pattern.match(path):
                return True
        return False

    def clear_matched_patterns(self):
        '''Clears matched patterns.'''
        self.matched_patterns = set()

    def highlight_pattern(self, pattern):
        '''Returns highlighted pattern.'''
        return '[41m' + pattern + '[0m'

    def highlight_line(self, line, match):
        '''Returns highlighted line according to match.'''
        assert match is not None
        return line[:match.start()] + self.highlight_pattern(match.group()) + line[match.end():]

    def check_diff(self, path, diff, counter):
        '''Check diff lines, print unexpected lines and gather matched patterns.'''
        for line in diff:
            if not counter.count_line(line):
                continue
            if not line.startswith('+'):
                # For diff, only check line added.
                continue
            line = line[1:]
            # Check line with each pattern.
            for pattern in self.unexpected_patterns:
                match = pattern.pattern.search(line)
                if match:
                    self.matched_patterns.add(pattern.name)
                    # Replace '\r' to '^M' to avoid dos line print error.
                    line_output = self.highlight_line(line, match).replace('\r', '^M')
                    self.output('%s:%d:%s:%s' % (path, counter.line_number, pattern.name, line_output))

    def print_matched_patterns(self):
        '''Print matched patterns.'''
        if self.matched_patterns:
            self.output('Patterns:')
            for pattern in self.unexpected_patterns:
                if pattern.name in self.matched_patterns:
                    self.output('%s: %s' % (pattern.name, pattern.description))

    def check(self, check_type=None, revisions=None):
        '''Check with type and revisions.'''
        raise NotImplementedError
