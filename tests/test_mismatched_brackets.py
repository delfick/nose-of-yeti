import re

import pytest


class TestMismatchedBrackets:
    def test_it_knows_about_mismatched_square_from_parenthesis(self):
        original = """
        def wat(self:
            pass

        things = "]"

        def things]self:
            pass
        """

        expected = re.escape(
            "Trying to close the wrong type of bracket. Found ']' (line 6, column 10) instead of closing a '(' (line 1, column 7)"
        )

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_mismatched_square_from_curly(self):
        original = """
        def wat{self:
            pass

        def things]self:
            pass
        """

        expected = re.escape(
            "Trying to close the wrong type of bracket. Found ']' (line 4, column 10) instead of closing a '{' (line 1, column 7)"
        )

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_mismatched_parenthesis_from_square(self):
        original = """
        def wat[self:
            pass

        def things)self:
            pass
        """

        expected = re.escape(
            "Trying to close the wrong type of bracket. Found ')' (line 4, column 10) instead of closing a '[' (line 1, column 7)"
        )

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_hanging_square(self):
        original = """
        def wat(self):
            pass

        def things]self:
            pass
        """

        expected = re.escape("Found a hanging ']' on line 4, column 10")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_hanging_parenthesis(self):
        original = """
        def wat(self)):
            pass
        """

        expected = re.escape("Found a hanging ')' on line 1, column 13")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_hanging_curly(self):
        original = """
        class Wat:
            def __init__(self):
                self.d = {1: 2}}
        """

        expected = re.escape("Found a hanging '}' on line 3, column 23")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_unclosed_parenthesis(self):
        original = """
        def thing(self):
            pass

        def wat(self:
            pass
        """

        expected = re.escape("Found an open '(' (line 4, column 7) that wasn't closed")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_unclosed_square(self):
        original = """
        def thing(self):
            pass

        things = [1, 2
        """

        expected = re.escape("Found an open '[' (line 4, column 9) that wasn't closed")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")

    def test_it_knows_about_unclosed_curly(self):
        original = """
        def thing(self):
            pass

        things = [1, 2]

        stuff = {1: 2
        """

        expected = re.escape("Found an open '{' (line 6, column 8) that wasn't closed")

        with pytest.raises(SyntaxError, match=expected):
            pytest.helpers.assert_conversion(original, "")
