from noseOfYeti.tokeniser.tracker import Tracker
from noseOfYeti.tokeniser.tokens import Tokens

from tokenize import generate_tokens


class Tokeniser:
    """Endpoint for tokenising a file"""

    def __init__(self, with_describe_attrs=True):
        self.with_describe_attrs = with_describe_attrs

    def translate(self, readline, result=None, no_imports=None):
        # Tracker to keep track of information as the file is processed
        self.tokens = Tokens()
        self.tracker = Tracker(result, self.tokens)

        try:
            # Looking at all the tokens
            with self.tracker.add_phase() as tracker:
                for tokenum, value, (srow, scol), _, _ in generate_tokens(readline):
                    tracker.next_token(tokenum, value, srow, scol)
        finally:
            # Complain about mismatched brackets
            self.tracker.raise_about_open_containers()

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.with_describe_attrs:
            self.tracker.make_describe_attrs()

        # Add lines to bottom of file to add __testname__ attributes
        self.tracker.make_method_names()

        # Return translated list of tokens
        return self.tracker.result
