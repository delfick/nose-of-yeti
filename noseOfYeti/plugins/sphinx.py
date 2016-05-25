from noseOfYeti.tokeniser.spec_codec import register_from_options
from noseOfYeti.plugins.support.spec_options import spec_options
from noseOfYeti.tokeniser.config import Default

import os

def enable(app):
    register_from_options(app.builder.config, spec_options, extractor=extract_options)

def normalise_options(template):
    env = os.environ
    for option, attributes in template.items():
        name = 'noy_{}'.format(option.replace('-', '_'))
        yield option, name, Default(attributes['default'](env))

def extract_options(template, config):
    for option, name, _ in normalise_options(template):
        yield option, getattr(config, name)

def setup(app):
    for option, name, default in normalise_options(spec_options):
        app.add_config_value(name, default, 'html')

    app.connect('builder-inited', enable)

