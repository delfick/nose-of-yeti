
from nose.plugins import Plugin

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

    def configure(self, options, conf):
        super(Plugin, self).configure(options, conf)
        if options.enabled:
            import tokeniser
