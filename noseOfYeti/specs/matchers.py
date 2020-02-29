from tokenize import untokenize
from should_dsl import matcher
from textwrap import dedent
from io import StringIO
import re


@matcher
class MatchRegexLines(object):
    name = "match_regex_lines"

    def __call__(self, radicand):
        self._radicand = radicand
        self.mismatched = ""
        return self

    def match(self, actual):
        self._actual = actual
        actual_lines = actual.strip().split("\n")
        radicand_lines = self._radicand.strip().split("\n")

        if len(actual_lines) != len(radicand_lines):
            self.mismatched = f"Expected same number of lines, got {len(actual_lines)} instead of {len(radicand_lines)}"
            return False

        for a, r in zip(actual_lines, radicand_lines):
            if not re.match(r, a):
                self.mismatched = f"'{r}'\ndid not match\n'{a}'"
                return False

        return True

    def message_for_failed_should(self):
        return f"expected \n{self._radicand}\n\n to match \n{self._actual}\n\n{self.mismatched}"

    def message_for_failed_should_not(self):
        return f"expected \n{self._radicand}\n\n to not match \n{self._actual}\n\n{self.mismatched}"


@matcher
class ResultInSyntaxError(object):

    name = "result_in_syntax_error"

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        tokeniser, self._actual = actual
        self._actual = dedent(self._actual).strip()
        s = StringIO(self._actual)
        try:
            tokeniser.translate(s.readline)
            self.error = "Expected a syntax error"
            return False
        except SyntaxError as error:
            if str(error) != self._radicand:
                self.error = (
                    f"Error message didn't match, expected\n{self._radicand}\ngot\n{str(error)}"
                )
                return False

        return True

    def message_for_failed_should(self):
        return self.error

    def message_for_failed_should_not(self):
        return self.error


@matcher
class ResultIn(object):

    name = "result_in"

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        tokeniser, self._actual = actual
        self._actual = dedent(self._actual).strip()
        s = StringIO(self._actual)
        try:
            tokens = tokeniser.translate(s.readline)
            self._expected = untokenize(tokens)
        finally:
            s.close()

        self._expected = dedent(self._expected).strip()
        self._radicand = dedent(self._radicand).strip()

        normalised_expected = []
        for line in self._expected.split("\n"):
            normalised_expected.append(line.rstrip())
        self._expected = "\n".join(normalised_expected)

        return self._expected == self._radicand

    def message_for_failed_should(self):
        r = lambda res: res.replace(" ", ".").replace("\t", "-")
        act = r(self._actual)
        rad = r(self._radicand)
        exp = r(self._expected)
        return f'expected "{act}"\n======================>\n"{rad}"\n\n======================$\n"{exp}"'

    def message_for_failed_should_not(self):
        r = lambda res: res.replace(" ", ".").replace("\t", "-")
        act = r(self._actual)
        rad = r(self._radicand)
        return f'expected "{act}"\n\tTo not translate to "{rad}"'
