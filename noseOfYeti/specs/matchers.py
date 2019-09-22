from tokenize import untokenize
from should_dsl import matcher
from textwrap import dedent
from six import StringIO
import re

@matcher
class MatchRegexLines(object):
    name = 'match_regex_lines'

    def __call__(self, radicand):
        self._radicand = radicand
        self.mismatched = ""
        return self

    def match(self, actual):
        self._actual = actual
        actual_lines = actual.strip().split("\n")
        radicand_lines = self._radicand.strip().split("\n")

        if len(actual_lines) != len(radicand_lines):
            self.mismatched = "Expected same number of lines, got {0} instead of {1}".format(len(actual_lines), len(radicand_lines))
            return False

        for a, r in zip(actual_lines, radicand_lines):
            if not re.match(r, a):
                self.mismatched = "'{0}'\ndid not match\n'{1}'".format(r, a)
                return False

        return True

    def message_for_failed_should(self):
        return 'expected \n{0}\n\n to match \n{1}\n\n{2}'.format(self._radicand, self._actual, self.mismatched)

    def message_for_failed_should_not(self):
        return 'expected \n{0}\n\n to not match \n{1}\n\n{2}'.format(self._radicand, self._actual, self.mismatched)

@matcher
class ResultInSyntaxError(object):

    name = 'result_in_syntax_error'

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        tokeniser, self._actual = actual
        self._actual = dedent(self._actual).strip()
        s = StringIO(self._actual)
        try:
            tokens = tokeniser.translate(s.readline)
            self.error = "Expected a syntax error"
            return False
        except SyntaxError as error:
            if str(error) != self._radicand:
                self.error = "Error message didn't match, expected\n{0}\ngot\n{1}".format(self._radicand, str(error))
                return False

        return True

    def message_for_failed_should(self):
        return self.error

    def message_for_failed_should_not(self):
        return self.error

@matcher
class ResultIn(object):

    name = 'result_in'

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
        for line in self._expected.split('\n'):
            normalised_expected.append(line.rstrip())
        self._expected = '\n'.join(normalised_expected)

        return self._expected == self._radicand

    def message_for_failed_should(self):
        return 'expected "{0}"\n======================>\n"{1}"\n\n======================$\n"{2}"'.format(
            *(res.replace(' ', '.').replace('\t', '-') for res in (self._actual, self._radicand, self._expected)))

    def message_for_failed_should_not(self):
        return 'expected "{0}"\n\tTo not translate to "{1}"'.format(
            *(res.replace(' ', '.').replace('\t', '-') for res in (self._actual, self._radicand)))

