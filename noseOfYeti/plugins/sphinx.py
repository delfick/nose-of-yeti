from sphinx.util.compat import Directive

from noseOfYeti.tokeniser import Tokeniser, TokeniserCodec, determine_imports
from support import spec_options

def enable(app):
    config = app.builder.config.values
    imports = determine_imports(
          extra_imports = ';'.join([d for d in config.get('noy_extra_import')[0] if d])
        , without_should_dsl = config.get('noy_without_should_dsl')[0]
        , with_default_imports = not config.get('noy_no_default_imports')[0]
        )
    
    tok = Tokeniser(
          default_kls = config.get('noy_default_kls')[0]
        , import_tokens = imports
        , wrapped_setup = options.wrapped_setup
        , with_describe_attrs = not config.get('noy_no_describe_attrs')[0]
        )
    
    TokeniserCodec(tok).register()

def setup(app):
    for option, default in spec_options.for_sphinx().items():
        name = 'noy_%s' % option.replace('-', '_')
        app.add_config_value(name, default, 'html')
    
    app.connect('builder-inited', enable)
