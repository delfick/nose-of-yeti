from noseOfYeti.tokeniser.spec_codec import register as enable


def setup(app):
    app.connect("builder-inited", enable)


__all__ = ["enable", "setup"]
