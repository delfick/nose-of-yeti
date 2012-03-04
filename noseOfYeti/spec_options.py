import os

spec_options = {
      'no-default-imports' : dict(
          default = lambda env :env.get('NOSE_NOY_NO_DEFAULT_IMPORTS') or False
        , action  = 'store_true'
        , dest    = 'no_default_imports'
        , help    = 'Turn off default imports for spec files'
        , type    = 'yn'
        )

    , 'no-describe-attrs' : dict(
          default = lambda env :env.get('NOSE_NOY_NO_DESCRIBE_ATTRS') or False
        , action  = 'store_true'
        , dest    = 'no_describe_attrs'
        , help    = 'Turn off giving describes a is_noy_spec attribute'
        , type    = 'yn'
        )

    , 'default-kls' : dict(
          default = lambda env :env.get('NOSE_NOY_DEFAULT_KLS') or 'object'
        , action  = 'store'
        , dest    = 'default_kls'
        , help    = 'Set default class for describes'
        , type    = 'string'
        )

    , 'extra-import' : dict(
          default = lambda env :[env.get('NOSE_NOY_EXTRA_IMPORTS')] or []
        , action  = 'append'
        , dest    = 'extra_import'
        , help    = '''Set extra default imports
                    (i.e. 'from something import *'
                          'import thing')
                    '''
        , type    = 'csv'
        )

    , 'ignore-kls' : dict(
          default = lambda env :[env.get('NOSE_NOY_IGNORE_KLS')] or []
        , action  = 'append'
        , dest    = 'ignore_kls'
        , help    = '''Set class name to ignore in wantMethod'''
        , type    = 'csv'
        )

    , 'without-should-dsl' : dict(
          default = lambda env :env.get('NOSE_NOY_WITHOUT_SHOULD_DSL') or False
        , action  = 'store_true'
        , dest    = 'without_should_dsl'
        , help    = '''Make it not try to import should-dsl'''
        , type    = 'yn'
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
        