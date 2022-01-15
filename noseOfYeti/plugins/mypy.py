from noseOfYeti.tokeniser.spec_codec import codec

from mypy.plugin import Plugin

spec_codec = codec()


class NoyPlugin(Plugin):
    pass


def plugin(version: str):
    spec_codec.register()
    return NoyPlugin
