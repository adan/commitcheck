#!/usr/bin/env python
# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Checker without argparse.'''

from __future__ import absolute_import, division, print_function, with_statement

import optparse
import os
import sys

from commitcheck.argutils import GIT_ARGUMENTS, git_get_type
from commitcheck.checkers import Pattern
from commitcheck.checkers.gitchecker import Checker


def main(argv=None):
    argv = sys.argv if argv is None else argv

    # Create parser and parse args.
    parser = optparse.OptionParser(description='Commit checker without argparse')
    for arg in GIT_ARGUMENTS:
        parser.add_option(*arg[0], **arg[1])
    (options, args) = parser.parse_args(argv[1:])
    check_type = git_get_type(options)
    if check_type is None:
        print('Unknown check type: %s' % (options.type))
        return 1

    # Setup to do check.
    path = os.getcwd()
    patterns = [
        Pattern(r'[ \t]+$', 'PTWS', 'Trailing whitespace'),
    ]
    checker = Checker(path, patterns, checks=[r'.*\.py'])
    checker.verbose = options.verbose
    return checker.check(check_type, args)


if __name__ == '__main__':
    sys.exit(main())
