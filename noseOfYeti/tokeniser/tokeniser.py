from tokenize import generate_tokens
from tracker import Tracker

class Tokeniser(object):
    """Endpoint for tokenising a file"""
    def __init__(self, defaultKls='object', withDescribeAttrs=True, importTokens=None):
        self.defaultKls = defaultKls
        self.importTokens = importTokens
        self.withDescribeAttrs = withDescribeAttrs

    ########################
    ###   TRANSLATE
    ########################

    def translate(self, readline, result=None):
        # Tracker to keep track of information as the file is processed
        self.tracker = Tracker(result, self.defaultKls)
        
        # Add import stuff at the top of the file
        if self.importTokens:
            self.tracker.addTokens(self.importTokens)

        # Looking at all the tokens
        with self.tracker.add_phase() as tracker:
            for tokenum, value, (_, scol), _, _ in generate_tokens(readline):
                self.tracker.next_token(tokenum, value, scol)

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.withDescribeAttrs:
            self.tracker.addTokens(self.tracker.makeDescribeAttrs())
        
        # Add lines to bottom of file to add __testname__ attributes
        self.tracker.addTokens(self.tracker.makeMethodNames())
        
        # Return translated list of tokens
        return self.tracker.result
