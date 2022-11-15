from noseOfYeti.tokeniser.spec_codec import register

from mypy.plugin import Plugin


class NoyPlugin(Plugin):
    pass


def plugin(version: str):
    register(transform=True)
    return NoyPlugin
