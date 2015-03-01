# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Git commit checking.'''

from __future__ import absolute_import, division, print_function, with_statement

import re

# Import git
try:
    from git import Repo
    from git.diff import Diffable
except ImportError:
    # 'git' could not be found or is not GitPython (Repo class should in git).
    raise ImportError('git(GitPython) could not be found in your PYTHONPATH.'
                      ' Please get and install GitPython.')

from .._compat import force_text
from . import Pattern, CheckTypes, LineCounter, BaseChecker


class DiffLineCounter(LineCounter):
    '''Git diff content line counter'''
    def __init__(self):
        super(DiffLineCounter, self).__init__()
        '''Git diff example:
        diff --git a/foo b/foo
        index 0c071e1..86e041d 100644
        --- a/foo
        +++ b/foo
        @@ -1,2 +1,3 @@
         foo
        +bar
         baz
        '''
        self.a_linum = 0
        self.b_linum = 0
        self.line_number_pattern = re.compile('''@@
            [ ]*[-](?P<a_start>[0-9]+?)(,(?P<a_count>[0-9]+?))?
            [ ]*[+](?P<b_start>[0-9]+?)(,(?P<b_count>[0-9]+?))?
            [ ]
            ''', re.VERBOSE | re.MULTILINE)

    def count_line(self, line):
        '''Returns False if just line numbers line.'''
        if line.startswith('@@'):
            (a_start, _, a_count, b_start, _, b_count) = self.line_number_pattern.match(line).groups()
            (self.a_linum, self.b_linum) = (int(a_start)-1, int(b_start)-1)
            return False
        if line.startswith('-'):
            self.a_linum += 1
        elif line.startswith('+'):
            self.b_linum += 1
        else:
            self.a_linum += 1
            self.b_linum += 1
        return True

    @property
    def line_number(self):
        '''Returns current line number.'''
        return self.b_linum


class Checker(BaseChecker):
    '''Git checker.'''
    def __init__(self, path, unexpected, ignores=None, checks=None):
        super(Checker, self).__init__(ignores, checks)
        self.repo = Repo(path)
        def pattern(pattern, index):
            return Pattern(re.compile(force_text(pattern.pattern)),
                           force_text(pattern.name or 'P%03d' % (index)),
                           force_text(pattern.description))
        self.unexpected_patterns = [pattern(p, i) for i, p in enumerate(unexpected)]

    def check_diffs(self, diffs):
        '''Check diffs and print unexpected lines and matched patterns.'''
        self.clear_matched_patterns()
        for diff in diffs:
            if diff.b_blob and self.need_check(diff.b_blob.path):
                self.verbose_output('Checking ' + diff.b_blob.path)
                self.check_diff(diff.b_blob.path, force_text(diff.diff).split('\n')[2:], DiffLineCounter())
        self.print_matched_patterns()
        return 1 if self.matched_patterns else 0

    def check(self, check_type=CheckTypes.CHECK_TYPE_GIT_DIFF, revisions=None):
        '''Check with type and revisions.'''
        head = revisions[0] if revisions else None
        commit = self.repo.commit(head) if head else self.repo.head.commit
        compare_base = commit
        against = None
        if check_type == CheckTypes.CHECK_TYPE_GIT_DIFF:
            # If diff, base is first revision or Index, against is None.
            compare_base = commit if head else self.repo.index
        elif check_type == CheckTypes.CHECK_TYPE_GIT_STAGED:
            # If staged, base is first revision or HEAD, against is Index (staged).
            against = Diffable.Index
        elif check_type == CheckTypes.CHECK_TYPE_GIT_TREE:
            # If tree, base is first revision, against is second revision or None.
            against = self.repo.commit(revisions[1]) if len(revisions) > 1 else None
        else:
            print('Unknown check type: %s' % (check_type))
            return 2
        diffs = compare_base.diff(against, create_patch=True)
        return self.check_diffs(diffs)
