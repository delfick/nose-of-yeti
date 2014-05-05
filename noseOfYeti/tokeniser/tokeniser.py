from noseOfYeti.tokeniser.tracker import Tracker
from noseOfYeti.tokeniser.tokens import Tokens

from tokenize import generate_tokens

class Tokeniser(object):
    """Endpoint for tokenising a file"""
    def __init__(self, default_kls='object', with_describe_attrs=True, import_tokens=None, wrapped_setup=False):
        self.default_kls = default_kls
        self.import_tokens = import_tokens
        self.wrapped_setup = wrapped_setup
        self.with_describe_attrs = with_describe_attrs

    ########################
    ###   TRANSLATE
    ########################

    def translate(self, readline, result=None, no_imports=None):
        # Tracker to keep track of information as the file is processed
        self.tokens = Tokens(self.default_kls)
        self.tracker = Tracker(result, self.tokens, self.wrapped_setup)

        # Add import stuff at the top of the file
        if self.import_tokens and no_imports is not True:
            self.tracker.add_tokens(self.import_tokens)

        # Looking at all the tokens
        with self.tracker.add_phase() as tracker:
            for tokenum, value, (_, scol), _, _ in generate_tokens(readline):
                tracker.next_token(tokenum, value, scol)

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.with_describe_attrs:
            self.tracker.add_tokens(self.tracker.make_describe_attrs())

        # If setups should be wrapped, then do this at the bottom
        if self.wrapped_setup:
            self.tracker.add_tokens(self.tracker.wrapped_setups())

        # Add lines to bottom of file to add __testname__ attributes
        self.tracker.add_tokens(self.tracker.make_method_names())

        # Return translated list of tokens
        return self.tracker.result

