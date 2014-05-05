from noseOfYeti.tokeniser.spec_codec import register_from_options
from noseOfYeti.tokeniser.config import Default
from .support.spec_options import spec_options
from .support.test_chooser import TestChooser

from nose.plugins import Plugin

def add_to_argparse(parser, env, template):
    parser_options = ['default', 'action', 'dest', 'help']
    for option, attributes in template.items():
        opts = dict((k, v) for k, v in attributes.items() if k in parser_options)
        opts['default'] = Default(opts['default'](env))
        parser.add_option('--noy-%s' % option, **opts)

def extract_options(template, options):
    for option, val in template.items():
        name = option.replace('-', '_')
        yield option, getattr(options, name)

class Plugin(Plugin):
    name = "noseOfYeti"

    def __init__(self, *args, **kwargs):
        self.test_chooser = TestChooser()
        super(Plugin, self).__init__(*args, **kwargs)

    def options(self, parser, env={}):
        super(Plugin, self).options(parser, env)
        add_to_argparse(parser, env, spec_options)

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
            self.done = {}
            self.enabled = True
            register_from_options(options, spec_options, extractor=extract_options)

