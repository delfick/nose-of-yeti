from noseOfYeti.tokeniser.config import Default
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
      'with-default-imports' : dict(
          default = default_from_env('NOSE_NOY_WITH_DEFAULT_IMPORTS', dflt=False)
        , action  = 'store_true'
        , dest    = 'with_default_imports'
        , help    = 'Turn on default imports for spec files'
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

    , 'wrapped-setup' : dict(
          default = default_from_env('NOSE_NOY_WRAPPED_SETUP', dflt=False)
        , action = 'store_true'
        , dest = 'wrapped_setup'
        , help = '''Wrap setups with lines at bottom of file instead of using noy_sup_* helpers'''
        , type = 'yn'
        )

    , 'config-file' : dict(
          default = default_from_env('NOSE_NOY_CONFIG_FILE', dflt='noy.json')
        , dest = 'config_file'
        , help = '''Location of a config file for nose of yeti'''
        )
    }

def extract_options_dict(template, options):
    """Extract options from a dictionary against the template"""
    for option, val in template.items():
        if options and option in options:
            yield option, options[option]
        else:
            yield option, Default(template[option]['default'](os.environ))

