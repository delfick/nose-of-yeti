"""
To be used as a pylint plugin to register the spec encoding
"""
from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

from noseOfYeti.tokeniser import Tokeniser, TokeniserCodec, determine_imports
from support import spec_options

class SpecRegister(BaseChecker):
    
    name = 'spec_register'
    __implements__ = IASTNGChecker

    msgs = {'W6969' : ('', '')}
    options = spec_options.for_pylint()
    priority = -1

    def open(self):
        imports = determine_imports(
              extra_imports = ';'.join([d for d in self.config.extra_import if d])
            , without_should_dsl = self.config.without_should_dsl
            , with_default_imports = not self.config.no_default_imports
            )
        
        tok = Tokeniser(
              default_kls = self.config.default_kls
            , import_tokens = imports
            , wrapped_setup = options.wrapped_setup
            , with_describe_attrs = not self.config.no_describe_attrs
            )
        
        TokeniserCodec(tok).register()
    
def register(linter):
    linter.register_checker(SpecRegister(linter))
