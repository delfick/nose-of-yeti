"""
To be used as a pylint plugin to register the spec encoding
"""
try:
    from pylint.interfaces import IASTNGChecker
except ImportError:
    IASTNGChecker = None

from pylint.checkers import BaseChecker

from noseOfYeti.tokeniser.spec_codec import register_from_options
from noseOfYeti.plugins.support.spec_options import spec_options
from noseOfYeti.tokeniser.config import Default

import os

class Empty(object): pass

def normalise_options(template):
    env = os.environ
    parser_options = ['default', 'help', 'type']
    for option, attributes in template.items():
        opts = dict((k, v) for k, v in attributes.items() if k in parser_options)
        opts['default'] = opts['default'](env)
        yield option, opts

def make_extractor(non_default):
    """
        Return us a function to extract options
        Anything not in non_default is wrapped in a "Default" object
    """
    def extract_options(template, options):
        for option, val in normalise_options(template):
            name = option.replace('-', '_')

            value = getattr(options, name)
            if option not in non_default:
                value = Default(value)

            yield name, value
    return extract_options

class SpecRegister(BaseChecker):

    name = 'NoyRegister'
    if IASTNGChecker:
        __implements__ = IASTNGChecker

    msgs = {'W6969' : ('', '')}
    options = list(normalise_options(spec_options))
    priority = -1

    def __init__(self, *args, **kwargs):
        self.specified = []
        super(SpecRegister, self).__init__(*args, **kwargs)

    def set_option(self, name, val, action=Empty, opts=Empty):
        """Determine which options were specified outside of the defaults"""
        if action is Empty and opts is Empty:
            self.specified.append(name)
            super(SpecRegister, self).set_option(name, val)
        else:
            super(SpecRegister, self).set_option(name, val, action, opts)

    def open(self):
        options = self.config
        register_from_options(options, spec_options, extractor=make_extractor(self.specified))

def register(linter):
    linter.register_checker(SpecRegister(linter))

