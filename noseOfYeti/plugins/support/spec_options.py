import os

def default_from_env(str, dflt=None, as_list=False):
    def get(env):
        arg_to_use = env.get('NOSE_NOY_EXTRA_IMPORTS')
        if arg_to_use is None:
            arg_to_use = dflt

        if as_list:
            if arg_to_use:
                return [arg_to_use]
            else:
                return []
        else:
            return dflt
    return get

spec_options = {
      'no-default-imports' : dict(
          default = default_from_env('NOSE_NOY_NO_DEFAULT_IMPORTS', dflt=False)
        , action  = 'store_true'
        , dest    = 'no_default_imports'
        , help    = 'Turn off default imports for spec files'
        , type    = 'yn'
        )

    , 'no-describe-attrs' : dict(
          default = default_from_env('NOSE_NOY_NO_DESCRIBE_ATTRS', dflt=False)
        , action  = 'store_true'
        , dest    = 'no_describe_attrs'
        , help    = 'Turn off giving describes a is_noy_spec attribute'
        , type    = 'yn'
        )

    , 'default-kls' : dict(
          default = default_from_env('NOSE_NOY_DEFAULT_KLS', dflt='object')
        , action  = 'store'
        , dest    = 'default_kls'
        , help    = 'Set default class for describes'
        , type    = 'string'
        )

    , 'extra-import' : dict(
          default = default_from_env('NOSE_NOY_EXTRA_IMPORTS', as_list=True)
        , action  = 'append'
        , dest    = 'extra_import'
        , help    = '''Set extra default imports
                    (i.e. 'from something import *'
                          'import thing')
                    '''
        , type    = 'csv'
        )

    , 'without-should-dsl' : dict(
          default = default_from_env('NOSE_NOY_WITHOUT_SHOULD_DSL', dflt=False)
        , action  = 'store_true'
        , dest    = 'without_should_dsl'
        , help    = '''Make it not try to import should-dsl'''
        , type    = 'yn'
        )
    
    , 'wrapped-setup' : dict(
          default = default_from_env('NOSE_NOY_WRAPPED_SETUP', dflt=False)
        , action = 'store_true'
        , dest = 'wrapped_setup'
        , help = '''Wrap setups with lines at bottom of file instead of using noy_sup_* helpers'''
        , type = 'yn'
        )
    }

def add_to_argparse(parser, env):
    parser_options = ['default', 'action', 'dest', 'help']
    for option, attributes in spec_options.items():
        opts = dict((k, v) for k, v in attributes.items() if k in parser_options)
        opts['default'] = opts['default'](env)
        parser.add_option('--noy-%s' % option, **opts)
    
def for_pylint():
    env = os.environ
    parser_options = ['default', 'help', 'type']
    options = []
    for option, attributes in spec_options.items():
        opts = dict((k, v) for k, v in attributes.items() if k in parser_options)
        opts['default'] = opts['default'](env)
        options.append((option, opts))
    return options

def for_sphinx():    
    env = os.environ
    options = {}
    for option, attributes in spec_options.items():
        options[option] = attributes['default'](env)
    
    return options
