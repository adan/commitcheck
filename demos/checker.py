#!/usr/bin/env python
# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Checker which requires argparse.'''

from __future__ import absolute_import, division, print_function, with_statement

import os
import sys

from commitcheck.argutils import git_create_parser, git_get_type
from commitcheck.checkers import Pattern
from commitcheck.checkers.gitchecker import Checker


def main(argv=None):
    argv = sys.argv if argv is None else argv

    # Create parser and parse args.
    parser = git_create_parser(description='Commit checker')
    args = parser.parse_args(argv[1:])
    check_type = git_get_type(args)
    if check_type is None:
        print('Unknown check type: %s' % (args.type))
        return 1

    # Setup to do check.
    path = os.getcwd()
    patterns = [
        Pattern(r'[ \t]+$', 'PTWS', 'Trailing whitespace'),
    ]
    checker = Checker(path, patterns, checks=[r'.*\.py'])
    checker.verbose = args.verbose
    return checker.check(check_type, args.revisions)


if __name__ == '__main__':
    sys.exit(main())
