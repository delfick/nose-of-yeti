from tokenize import untokenize
from should_dsl import matcher
from textwrap import dedent
from six import StringIO

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

