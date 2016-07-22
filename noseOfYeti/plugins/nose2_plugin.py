from noseOfYeti.tokeniser.spec_codec import register_from_options
from noseOfYeti.plugins.support.spec_options import spec_options
from noseOfYeti.plugins.support.test_chooser import TestChooser
from noseOfYeti.tokeniser.config import Default

from nose2.events import Plugin

import logging
import sys
import os

log = logging.getLogger('nose2.plugins.noseOfYeti')

def extract_options(template, options):
    for option, val in template.items():
        yield option, options.get(option)

class NoseOfYetiPlugin(Plugin):
    configSection = 'noseOfYeti'

    def __init__(self):
        self.test_chooser = TestChooser()
        default_ignore_kls = []
        if "NOSE_NOY_IGNORE_KLS" in os.environ:
            default_ignore_kls.extend(os.environ["NOSE_NOY_IGNORE_KLS"].split(","))
        self.ignore_kls = self.config.as_list('ignore-kls', default=default_ignore_kls)
        self.always_on = self.config.as_bool('always-on', default=False)

        parser_options = ['default', 'action', 'dest', 'help']
        for option, attributes in spec_options.items():
            action = attributes.get("action", "store")
            default = attributes.get("default")

            if action == "store_true":
                action = "as_bool"
                default = False
            elif action == "store_false":
                action = "as_bool"
                default = True
            elif action == "append":
                action = "as_list"
                default = attributes.get("default", [])
            elif action == "store":
                action = "as_str"
                default = attributes.get("default")

            if callable(default):
                default = default(os.environ)
            setattr(self, option.replace("-", "_"), getattr(self.config, action)(option, default=Default(default)))

    def handleFile(self, event):
        if not getattr(self, "_configured", False):
            self._configured = True
            self.enable()

    def loadTestsFromModule(self, event):
        self.test_chooser.new_module()
        if hasattr(event.module, "__package__"):
            pkg = sys.modules.get(event.module.__package__)
            if getattr(pkg, "__test__", None) is False:
                event.handled = True

    def getTestCaseNames(self, event):
        names = filter(event.isTestMethod, dir(event.testCase))
        methods = [(name, getattr(event.testCase, name)) for name in names]
        event.handled = True
        return [name for name, method in methods if self.test_chooser.consider(method, self.ignore_kls) is not False]

    def enable(self):
        self.done = {}
        options = dict((option, getattr(self, option.replace('-', '_'))) for option in spec_options)
        register_from_options(options, spec_options, extractor=extract_options)

