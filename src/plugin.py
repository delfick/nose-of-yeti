from nose.plugins import Plugin
from tokeniser import Tokeniser

class Plugin(Plugin):
    enabled = True
    name = "noseOfYeti"
    score = 0

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

    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)
        if options.enabled:
            tok = Tokeniser( withDefaultImports = not options.noDefaultImports
                           , extraImports       = ';'.join([d for d in options.extraImport if d])
                           , defaultKls         = options.defaultKls
                           )
            tok.register()
