from nose.plugins import Plugin

from noseOfYeti.tokeniser.chooser import TestChooser
from noseOfYeti.tokeniser.spec_codec import register


class Plugin(Plugin):
    name = "noseOfYeti"

    def __init__(self, *args, **kwargs):
        self.test_chooser = TestChooser()
        super(Plugin, self).__init__(*args, **kwargs)

    def options(self, parser, env={}):
        super(Plugin, self).options(parser, env)

        parser.add_option(
            "--with-noy",
            default=False,
            action="store_true",
            dest="enabled",
            help="Enable nose of yeti",
        )

    def wantModule(self, mod):
        self.test_chooser.new_module()

    def wantMethod(self, method):
        return self.test_chooser.consider(method)

    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)

        if options.enabled:
            self.done = {}
            self.enabled = True
            register(transform=True)
