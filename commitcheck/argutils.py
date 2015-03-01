# Copyright (c) 2015 Xiaofan Li
# License: MIT

'''Utils to create and setup argument parser for checker.'''

from __future__ import absolute_import, division, print_function, with_statement

try:
    import argparse
    _ARGPARSE_AVAILABLE = True
except ImportError:
    _ARGPARSE_AVAILABLE = False

from .checkers import CheckTypes


GIT_ARGUMENTS = (
    (('-v', '--verbose'), {'action': 'store_true', 'help': 'More verbose output'}),
    (('-t', '--type'), {'default': 'diff', 'help': ('Check type: [diff|staged|tree],'
                                                    ' -t diff [<commit>],'
                                                    ' -t staged [<commit>],'
                                                    ' -t tree [<base> [<against>]]')}),
)


class ParserCreator(object):
    '''Generic parser creator.'''
    def create_parser(self, *args, **kwargs):
        '''Create argument parser with args and kwargs.'''
        return argparse.ArgumentParser(*args, **kwargs)

    def get_parser(self, *args, **kwargs):
        '''Get parser in kwargs if not None, or else create a parser.'''
        parser = kwargs.pop('parser', None)
        # Use *args and **kwargs to create parser if parser is None.
        if parser is None:
            parser = self.create_parser(*args, **kwargs)
        elif kwargs:
            raise TypeError('If parser is given, other parameters should not be passed.')
        return parser

    def setup_parser(self, parser):
        '''Add arguments to parser.'''
        raise NotImplementedError

    def create(self, *args, **kwargs):
        '''Get and setup parser.'''
        parser = self.get_parser(*args, **kwargs)
        return self.setup_parser(parser)


class GitParserCreator(ParserCreator):
    '''Git parser creator.'''
    def setup_parser(self, parser):
        '''Add git arguments to parser.'''
        extra_arguments = (
            (('revisions'), {'nargs': argparse.REMAINDER, 'help': 'Check revisions'}),
        )
        for arg in GIT_ARGUMENTS + extra_arguments:
            parser.add_argument(*(arg[0] if isinstance(arg[0], tuple) else (arg[0],)), **arg[1])
        return parser


def git_create_parser(*args, **kwargs):
    '''git_create_parser(parser=parser, ...) -> parser'''
    if not _ARGPARSE_AVAILABLE:
        raise ImportError('argparse could not be found in your PYTHONPATH.'
                          ' Please install argparse or use optparse instead.')
    return GitParserCreator().create(*args, **kwargs)


def git_get_type(args):
    '''Get git type option.'''
    if args.type == 'diff':
        return CheckTypes.CHECK_TYPE_GIT_DIFF
    elif args.type == 'staged':
        return CheckTypes.CHECK_TYPE_GIT_STAGED
    elif args.type == 'tree':
        return CheckTypes.CHECK_TYPE_GIT_TREE
    else:
        return None
