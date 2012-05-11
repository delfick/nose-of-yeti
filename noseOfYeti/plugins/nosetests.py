from noseOfYeti.tokeniser import Tokeniser, TokeniserCodec, determine_imports
from support.test_chooser import TestChooser
from support import spec_options

from nose.plugins import Plugin

class Plugin(Plugin):
    name = "noseOfYeti"
    
    def __init__(self, *args, **kwargs):
        self.test_chooser = TestChooser()
        super(Plugin, self).__init__(*args, **kwargs)
    
    def options(self, parser, env={}):
        super(Plugin, self).options(parser, env)
        spec_options.add_to_argparse(parser, env)
        
        parser.add_option('--with-noy'
            , default = False
            , action  = 'store_true'
            , dest    = 'enabled'
            , help    = 'Enable nose of yeti'
            )
        
        default_ignore_kls = []
        if 'NOSE_NOY_IGNORE_KLS' in env:
            default_ignore_kls.append(env['NOSE_NOY_IGNORE_KLS'].split(','))
        
        parser.add_option('--noy-ignore-kls'
            , default = default_ignore_kls
            , action  = 'append'
            , dest    = 'ignore_kls'
            , help    = 'Set class name to ignore in wantMethod'
            )
    
    def wantModule(self, mod):
        self.test_chooser.new_module()
    
    def wantMethod(self, method):
        return self.test_chooser.consider(method, self.ignore_kls)
    
    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)
        self.ignore_kls = options.ignore_kls
        if options.enabled:
            self.enabled = True
            self.done = {}
            imports = determine_imports(
                  extra_imports = ';'.join([d for d in options.extra_import if d])
                , without_should_dsl = options.without_should_dsl
                , with_default_imports = not options.no_default_imports
                )
            
            tok = Tokeniser(
                  default_kls = options.default_kls
                , import_tokens = imports
                , wrapped_setup = options.wrapped_setup
                , with_describe_attrs = not options.no_describe_attrs
                )
            
            TokeniserCodec(tok).register()
