"""
To be used as a pylint plugin to register the spec encoding
"""
try:
    from pylint.interfaces import IASTNGChecker
except ImportError:
    IASTNGChecker = None

from pylint.checkers import BaseChecker

from noseOfYeti.tokeniser.spec_codec import register as noy_register


class SpecRegister(BaseChecker):

    name = "NoyRegister"
    if IASTNGChecker:
        __implements__ = IASTNGChecker

    msgs = {"W6969": ("", "")}
    priority = -1

    def __init__(self, *args, **kwargs):
        self.specified = []
        super(SpecRegister, self).__init__(*args, **kwargs)

    def open(self):
        noy_register()


def register(linter):
    linter.register_checker(SpecRegister(linter))
