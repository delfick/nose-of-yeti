from tokeniser import Tokeniser, TokeniserCodec, determineImports
from test_chooser import TestChooser
from nose.plugins import Plugin
from inspect import getmembers

class Plugin(Plugin):
    name = "noseOfYeti"
    
    def __init__(self, *args, **kwargs):
        self.test_chooser = TestChooser()
        super(Plugin, self).__init__(*args, **kwargs)

    def options(self, parser, env={}):
        super(Plugin, self).options(parser, env)
        parser.add_option(
              '--with-noy'
            , default = False
            , action  = 'store_true'
            , dest    = 'enabled'
            , help    = 'Enable nose of yeti'
            )
            
        parser.add_option(
              '--noy-no-default-imports'
            , default = env.get('NOSE_NOY_NO_DEFAULT_IMPORTS') or False
            , action  = 'store_true'
            , dest    = 'noDefaultImports'
            , help    = 'Turn off default imports for spec files'
            )
            
        parser.add_option(
              '--noy-no-describe-attrs'
            , default = env.get('NOSE_NOY_NO_DESCRIBE_ATTRS') or False
            , action  = 'store_true'
            , dest    = 'noDescribeAttrs'
            , help    = 'Turn off giving describes a is_noy_spec attribute'
            )
            
        parser.add_option(
              '--noy-default-kls'
            , default = env.get('NOSE_NOY_DEFAULT_KLS') or 'object'
            , action  = 'store'
            , dest    = 'defaultKls'
            , help    = 'Set default class for describes'
            )
            
        parser.add_option(
              '--noy-extra-import'
            , default = [env.get('NOSE_NOY_EXTRA_IMPORTS')] or []
            , action  = 'append'
            , dest    = 'extraImport'
            , help    = '''Set extra default imports 
                        (i.e. 'from something import *'
                              'import thing')
                        '''
            )
            
        parser.add_option(
              '--noy-ignore-kls'
            , default = [env.get('NOSE_NOY_IGNORE_KLS')] or []
            , action  = 'append'
            , dest    = 'ignoreKls'
            , help    = '''Set class name to ignore in wantMethod'''
            )
            
        parser.add_option(
              '--without-should-dsl'
            , default = env.get('NOSE_NOY_WITHOUT_SHOULD_DSL') or False
            , action  = 'store_true'
            , dest    = 'withoutShouldDsl'
            , help    = '''Make it not try to import should-dsl'''
            )
    
    def wantModule(self, mod):
        self.test_chooser.new_module()
        
    def wantMethod(self, method):
        return self.test_chooser.consider(method, self.ignoreKls)
        
    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)
        self.ignoreKls = options.ignoreKls
        if options.enabled:
            self.enabled = True
            self.done = {}
            imports = determineImports(
                  extraImports = ';'.join([d for d in options.extraImport if d])
                , withoutShouldDsl = options.withoutShouldDsl
                , withDefaultImports = not options.noDefaultImports
                )
            
            tok = Tokeniser(
                  defaultKls = options.defaultKls
                , importTokens = imports
                , withDescribeAttrs = not options.noDescribeAttrs
                )
            
            TokeniserCodec(tok).register()
