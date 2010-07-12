from nose.plugins import Plugin
from tokeniser import Tokeniser

class Plugin(Plugin):
    name = "noseOfYeti"

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
    
    def wantModule(self, mod):
        self.done = {}
        
    def wantMethod(self, method):
        
        if method.__name__.startswith("ignore__"):
            return False
        
        kls = method.im_class
               
        if kls.__name__ in self.ignoreKls:
            return False
        
        if hasattr(kls, 'is_noy_spec'):
            if method.__name__ in kls.__dict__ \
            and not method.__name__.startswith("setUp") \
            and not method.__name__.startswith("tearDown") :

                key = '%s.%s' % (kls.__name__, method.__name__)
                if key not in self.done:
                    self.done[key] = True
                    return True
                
                return False
        else:
            return True
        
        return False
        
    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)
        self.ignoreKls = options.ignoreKls
        if options.enabled:
            self.enabled = True
            self.done = {}
            tok = Tokeniser( withDefaultImports = not options.noDefaultImports
                           , withDescribeAttrs  = not options.noDescribeAttrs
                           , extraImports       = ';'.join([d for d in options.extraImport if d])
                           , defaultKls         = options.defaultKls
                           )
            tok.register()
