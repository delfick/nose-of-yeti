"""
To be used as a pylint plugin to register the spec encoding
"""
from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

from noseOfYeti.tokeniser.spec_codec import register_from_options
from noseOfYeti.tokeniser.config import Default
from support.spec_options import spec_options

import os

def normalise_options(template):
    env = os.environ
    parser_options = ['default', 'help', 'type']
    for option, attributes in template.items():
        opts = dict((k, v) for k, v in attributes.items() if k in parser_options)
        opts['default'] = Default(opts['default'](env))
        yield option, opts

def extract_options(template, options):
    for option, val in normalise_options(template):
        name = option.replace('-', '_')
        yield option, getattr(options, name)

class SpecRegister(BaseChecker):

    name = 'spec_register'
    __implements__ = IASTNGChecker

    msgs = {'W6969' : ('', '')}
    options = dict(normalise_options(spec_options))
    priority = -1

    def open(self):
        options = self.config
        register_from_options(options, spec_options, extractor=extract_options)

def register(linter):
    linter.register_checker(SpecRegister(linter))

