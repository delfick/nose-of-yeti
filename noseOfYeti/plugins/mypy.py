from mypy.plugin import Plugin

from noseOfYeti.tokeniser.spec_codec import register


class NoyPlugin(Plugin):
    pass


def plugin(version: str):
    register(transform=True)
    return NoyPlugin
