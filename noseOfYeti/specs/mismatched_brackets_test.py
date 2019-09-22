from noseOfYeti.tokeniser import Tokeniser
from should_dsl import should

class TestMismatchedBrackets(object):
    def test_it_knows_about_mismatched_brackets(self):
        txt = '''
        def wat(self:
            pass

        things = "]"

        def things]self:
            pass
        '''

        expected = "Trying to close the wrong type of bracket. Found ']' (line 6, column 10) instead of closing a '(' (line 1, column 7)"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        def wat{self:
            pass

        def things]self:
            pass
        '''

        expected = "Trying to close the wrong type of bracket. Found ']' (line 4, column 10) instead of closing a '{' (line 1, column 7)"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        def wat[self:
            pass

        def things)self:
            pass
        '''

        expected = "Trying to close the wrong type of bracket. Found ')' (line 4, column 10) instead of closing a '[' (line 1, column 7)"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

    def test_it_knows_about_hanging_brackets(self):
        txt = '''
        def wat(self):
            pass

        def things]self:
            pass
        '''

        expected = "Found a hanging ']' on line 4, column 10"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        def wat(self)):
            pass
        '''

        expected = "Found a hanging ')' on line 1, column 13"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        class Wat:
            def __init__(self):
                self.d = {1: 2}}
        '''

        expected = "Found a hanging '}' on line 3, column 23"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

    def test_it_knows_about_unclosed_brackets(self):
        txt = '''
        def thing(self):
            pass

        def wat(self:
            pass
        '''

        expected = "Found an open '(' (line 4, column 7) that wasn't closed"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        def thing(self):
            pass

        things = [1, 2
        '''

        expected = "Found an open '[' (line 4, column 9) that wasn't closed"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)

        txt = '''
        def thing(self):
            pass

        things = [1, 2]

        stuff = {1: 2
        '''

        expected = "Found an open '{' (line 6, column 8) that wasn't closed"
        (Tokeniser(), txt) |should| result_in_syntax_error(expected)
